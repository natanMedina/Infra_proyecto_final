# ================================
# LIBRERÍAS Y DEPENDENCIAS
# ================================
import ray  # Computación distribuida y paralela
import pandas as pd  # Manipulación de datos
import numpy as np  # Cálculos numéricos
import yfinance as yf  # Descarga de datos financieros
import os
from typing import List, Tuple, Dict  # Tipado estático

# ================================
# FUNCIONES DE VALIDACIÓN
# ================================

@ray.remote
def validate_symbol(symbol: str, start='2021-01-01', end='2023-03-01') -> Tuple[str, bool]:
    """
    Intenta descargar datos de un símbolo financiero en un rango de fechas usando yfinance.
    Devuelve una tupla con el símbolo y un booleano indicando si los datos existen.
    Esta función se ejecuta en paralelo con Ray.
    """
    try:
        df = yf.download(symbol, start=start, end=end, progress=False)
        return (symbol, not df.empty)
    except Exception:
        return (symbol, False)

# ================================
# CARGA Y PREPARACIÓN DE DATOS
# ================================

def load_sentiment_data(path: str) -> pd.DataFrame:
    """
    Carga un CSV con datos de sentimiento de redes sociales.
    Filtra tuits con bajo engagement y calcula una métrica de ratio de engagement.
    Devuelve un DataFrame indexado por fecha y símbolo.
    """
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date', 'symbol'])
    df['engagement_ratio'] = df['twitterComments'] / df['twitterLikes']
    df = df[(df['twitterLikes'] > 20) & (df['twitterComments'] > 10)]
    return df

# ================================
# FILTRADO Y RANKEO POR CRITERIO
# ================================

def filter_and_rank(sentiment_df: pd.DataFrame, criterio: str = 'engagement_ratio') -> pd.DataFrame:
    """
    Filtra y ranquea activos financieros según un criterio de sentimiento (por defecto: engagement_ratio).
    Selecciona los 5 mejores por mes. Devuelve un DataFrame multi-índice (fecha, símbolo).
    """
    if criterio not in sentiment_df.columns:
        raise ValueError(f"La columna '{criterio}' no se encuentra disponible en el DataFrame.")

    aggragated_df = (
        sentiment_df.reset_index('symbol')
        .groupby([pd.Grouper(freq='ME'), 'symbol'])[[criterio]]
        .mean()
    )
    aggragated_df['rank'] = (
        aggragated_df.groupby(level=0)[criterio]
        .transform(lambda x: x.rank(ascending=False))
    )
    filtered_df = aggragated_df[aggragated_df['rank'] < 6].copy()  # Top 5 activos
    filtered_df = filtered_df.reset_index(level=1)
    filtered_df.index = filtered_df.index + pd.DateOffset(1)  # Avanza la fecha al primer día del mes siguiente
    return filtered_df.reset_index().set_index(['date', 'symbol'])

# ================================
# CONSTRUCCIÓN DE PORTAFOLIO
# ================================

def get_filtered_dates(filtered_df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Construye un diccionario donde las llaves son fechas (string)
    y los valores son listas de símbolos seleccionados para ese mes.
    """
    dates = filtered_df.index.get_level_values('date').unique().tolist()
    fixed_dates = {}
    for d in dates:
        fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
    return fixed_dates

def validate_symbols_parallel(symbols: List[str]) -> Tuple[List[str], List[str]]:
    """
    Valida múltiples símbolos en paralelo con Ray.
    Devuelve dos listas: símbolos válidos y no válidos.
    """
    results = ray.get([validate_symbol.remote(s) for s in symbols])
    valid = [s for s, ok in results if ok]
    failed = [s for s, ok in results if not ok]
    return valid, failed

@ray.remote
def download_prices(symbols: List[str], start: str = '2021-01-01', end: str = '2023-03-01') -> pd.DataFrame:
    """
    Descarga precios históricos de los símbolos seleccionados usando yfinance.
    Ejecutado en paralelo con Ray.
    """
    return yf.download(tickers=symbols, start=start, end=end, progress=False)

def calculate_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula retornos logarítmicos diarios a partir de precios de cierre.
    """
    return np.log(prices_df['Close']).diff().dropna()

@ray.remote
def build_monthly_portfolio(returns_df: pd.DataFrame, start_date: str, cols: List[str]) -> pd.DataFrame:
    """
    Construye un portafolio mensual igual ponderado para los activos seleccionados.
    Calcula el retorno promedio diario del portafolio para ese mes.
    """
    end_date = (pd.to_datetime(start_date) + pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
    valid_cols = [c for c in cols if c in returns_df.columns]
    if not valid_cols:
        return pd.DataFrame()
    temp_df = returns_df[start_date:end_date][valid_cols].mean(axis=1).to_frame('portfolio_returns')
    return temp_df

def assemble_portfolio(returns_df: pd.DataFrame, fixed_dates: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Ejecuta la construcción del portafolio mensual en paralelo para todas las fechas.
    Une todos los portafolios mensuales en un único DataFrame.
    """
    futures = [build_monthly_portfolio.remote(returns_df, d, cols) for d, cols in fixed_dates.items()]
    monthly_dfs = ray.get(futures)
    portfolio_df = pd.concat(monthly_dfs, axis=0)
    return portfolio_df

def get_benchmark_returns(start: str = '2021-01-01', end: str = '2023-03-01') -> pd.Series:
    """
    Descarga los retornos logarítmicos diarios del ETF QQQ como benchmark (NASDAQ 100).
    """
    qqq_df = yf.download(tickers='QQQ', start=start, end=end, progress=False)
    return np.log(qqq_df['Close']).diff()

def calculate_cumulative_returns(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el retorno acumulado exponencial del portafolio.
    """
    return np.exp(np.log1p(portfolio_df).cumsum()).sub(1)

# ================================
# PIPELINE PRINCIPAL
# ================================

def run_pipeline(criterio: str = "engagement_ratio", path: str = "datasets/sentiment_data.csv", tracker=None) -> pd.DataFrame:
    """
    Ejecuta toda la lógica de la estrategia:
    1. Carga y filtra datos de sentimiento.
    2. Rankeo mensual por criterio.
    3. Validación de símbolos y descarga de precios.
    4. Construcción de portafolio mensual.
    5. Comparación con benchmark (QQQ).
    6. Guardado del retorno acumulado en CSV.

    Parámetros:
    - criterio: Métrica de sentimiento para ranquear (ej: engagement_ratio).
    - path: Ruta al archivo CSV de sentimiento.
    - tracker: Objeto remoto para actualizar progreso (opcional).
    """
    if tracker:
        ray.get(tracker.set_status.remote("Cargando información de sentimiento", 5))
    sentiment_df = load_sentiment_data(path)

    if tracker:
        ray.get(tracker.set_status.remote(f"Aplicando filtro y ranking por {criterio}", 15))
    filtered_df = filter_and_rank(sentiment_df, criterio)

    if tracker:
        ray.get(tracker.set_status.remote("Procesando fechas de portafolio", 25))
    fixed_dates = get_filtered_dates(filtered_df)

    symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()

    if tracker:
        ray.get(tracker.set_status.remote("Verificando disponibilidad de símbolos", 35))
    valid_symbols, _ = validate_symbols_parallel(symbols)

    if tracker:
        ray.get(tracker.set_status.remote("Obteniendo precios del mercado", 50))
    prices_df = ray.get(download_prices.remote(valid_symbols))

    if tracker:
        ray.get(tracker.set_status.remote("Calculando series de retornos", 65))
    returns_df = calculate_returns(prices_df)

    if tracker:
        ray.get(tracker.set_status.remote("Generando portafolios mensuales", 80))
    portfolio_df = assemble_portfolio(returns_df, fixed_dates)

    if tracker:
        ray.get(tracker.set_status.remote("Incorporando benchmark QQQ", 90))
    benchmark_series = get_benchmark_returns()
    portfolio_df['nasdaq_return'] = benchmark_series

    if tracker:
        ray.get(tracker.set_status.remote("Finalizando con cálculo de retorno acumulado", 100))
    cumulative_df = calculate_cumulative_returns(portfolio_df)

    os.makedirs("output", exist_ok=True)
    cumulative_df.to_csv("output/cumulative_returns.csv")

    return cumulative_df

# ================================
# TRACKER DE PROGRESO CON RAY
# ================================

@ray.remote
class ProgressTracker:
    """
    Clase remota que actúa como tracker de progreso en tiempo real para mostrar
    el estado de ejecución del pipeline.
    """
    def _init_(self):
        self.status = "Configurando entorno..."
        self.progress = 0

    def set_status(self, status: str, progress: int):
        self.status = status
        self.progress = progress

    def get_status(self):
        return {"status": self.status, "progress": self.progress}