# Importación de bibliotecas necesarias
import time  # Para medir tiempos de ejecución
import pandas as pd  # Para manejo de datos en DataFrames
import numpy as np  # Para cálculos numéricos
import psutil  # Para monitorear uso de CPU
import yfinance as yf  # Para descargar datos financieros
import os  # Para manejo de directorios y archivos
import ray  # Para paralelización de tareas
import matplotlib.pyplot as plt  # Para visualización de gráficos
from typing import List, Tuple, Dict  # Para anotaciones de tipo
from ray_task.sentiment import (  # Importación de funciones paralelas personalizadas
    load_sentiment_data,
    filter_and_rank,
    get_filtered_dates,
    validate_symbols_parallel,
    download_prices,
    calculate_returns,
    assemble_portfolio,
    get_benchmark_returns,
    calculate_cumulative_returns
)

# Función para medir uso de la CPU
def measure_cpu_usage():
    """Mide y retorna el porcentaje de uso actual de la CPU"""
    return psutil.cpu_percent(interval=1)

# Función secuencial para validar un símbolo financiero
def validate_symbol_sequential(symbol: str, start='2021-01-01', end='2023-03-01') -> Tuple[str, bool]:
    """
    Valida si un símbolo de acción existe y tiene datos en Yahoo Finance
    
    Args:
        symbol: Símbolo de la acción a validar (ej: 'AAPL')
        start: Fecha de inicio en formato 'YYYY-MM-DD'
        end: Fecha de fin en formato 'YYYY-MM-DD'
    
    Returns:
        Tupla con (símbolo, booleano) indicando si es válido
    """
    try:
        # Intenta descargar datos del símbolo
        df = yf.download(symbol, start=start, end=end, progress=False)
        # Retorna True si el DataFrame no está vacío
        return (symbol, not df.empty)
    except Exception:
        # Si hay error, retorna False
        return (symbol, False)

# Función secuencial para validar múltiples símbolos
def validate_symbols_sequential(symbols: List[str]) -> Tuple[List[str], List[str]]:
    """
    Valida una lista de símbolos de forma secuencial
    
    Args:
        symbols: Lista de símbolos a validar
    
    Returns:
        Dos listas: (símbolos válidos, símbolos fallidos)
    """
    valid = []  # Lista para símbolos válidos
    failed = []  # Lista para símbolos fallidos
    
    # Itera sobre cada símbolo en la lista
    for symbol in symbols:
        # Valida el símbolo actual
        valid_symbol, is_valid = validate_symbol_sequential(symbol)
        if is_valid:
            valid.append(valid_symbol)  # Agrega a válidos si es correcto
        else:
            failed.append(valid_symbol)  # Agrega a fallidos si no
    
    return valid, failed

# Función para cargar datos de sentimiento
def load_sentiment_data_sequential(path: str) -> pd.DataFrame:
    """
    Carga y procesa datos de sentimiento desde un archivo CSV
    
    Args:
        path: Ruta al archivo CSV con datos de sentimiento
    
    Returns:
        DataFrame procesado con datos de sentimiento
    """
    # Carga el archivo CSV
    df = pd.read_csv(path)
    # Convierte la columna 'date' a datetime
    df['date'] = pd.to_datetime(df['date'])
    # Establece índice compuesto por fecha y símbolo
    df = df.set_index(['date', 'symbol'])
    # Calcula ratio de engagement (comentarios/likes)
    df['engagement_ratio'] = df['twitterComments'] / df['twitterLikes']
    # Filtra registros con mínimo de likes y comentarios
    df = df[(df['twitterLikes'] > 20) & (df['twitterComments'] > 10)]
    
    return df

# Función para filtrar y rankear datos de sentimiento
def filter_and_rank_sequential(sentiment_df: pd.DataFrame, criterio: str = 'engagement_ratio') -> pd.DataFrame:
    """
    Filtra y rankea los datos de sentimiento según un criterio
    
    Args:
        sentiment_df: DataFrame con datos de sentimiento
        criterio: Columna a usar para el ranking
    
    Returns:
        DataFrame filtrado y rankeado
    """
    # Verifica que el criterio exista en el DataFrame
    if criterio not in sentiment_df.columns:
        raise ValueError(f"Columna '{criterio}' no encontrada en el DataFrame")

    # Agrupa por mes y símbolo, calculando la media del criterio
    aggragated_df = (
        sentiment_df.reset_index('symbol')
        .groupby([pd.Grouper(freq='ME'), 'symbol'])[[criterio]]
        .mean()
    )
    
    # Calcula el ranking de cada símbolo por mes
    aggragated_df['rank'] = (
        aggragated_df.groupby(level=0)[criterio]
        .transform(lambda x: x.rank(ascending=False))
    )
    
    # Filtra solo los top 5 de cada mes (rank < 6)
    filtered_df = aggragated_df[aggragated_df['rank'] < 6].copy()
    # Resetea el nivel de símbolo del índice
    filtered_df = filtered_df.reset_index(level=1)
    # Ajusta las fechas al inicio del mes siguiente
    filtered_df.index = filtered_df.index + pd.DateOffset(1)
    
    # Retorna el DataFrame reorganizado
    return filtered_df.reset_index().set_index(['date', 'symbol'])

# Función para obtener fechas y símbolos filtrados
def get_filtered_dates_sequential(filtered_df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Organiza los símbolos filtrados por fecha
    
    Args:
        filtered_df: DataFrame con datos ya filtrados
    
    Returns:
        Diccionario con {fecha: [símbolos]}
    """
    # Obtiene las fechas únicas del índice
    dates = filtered_df.index.get_level_values('date').unique().tolist()
    fixed_dates = {}  # Diccionario para almacenar resultados
    
    # Para cada fecha, obtiene sus símbolos correspondientes
    for d in dates:
        fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
    
    return fixed_dates

# Función para descargar precios de acciones
def download_prices_sequential(symbols: List[str], start: str = '2021-01-01', end: str = '2023-03-01') -> pd.DataFrame:
    """
    Descarga precios históricos para una lista de símbolos
    
    Args:
        symbols: Lista de símbolos a descargar
        start: Fecha de inicio en formato 'YYYY-MM-DD'
        end: Fecha de fin en formato 'YYYY-MM-DD'
    
    Returns:
        DataFrame con precios históricos
    """
    return yf.download(tickers=symbols, start=start, end=end, progress=False)

# Función para calcular retornos logarítmicos
def calculate_returns_sequential(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula retornos logarítmicos diarios
    
    Args:
        prices_df: DataFrame con precios de cierre
    
    Returns:
        DataFrame con retornos diarios
    """
    return np.log(prices_df['Close']).diff().dropna()

# Función para construir portafolio mensual
def build_monthly_portfolio_sequential(returns_df: pd.DataFrame, start_date: str, cols: List[str]) -> pd.DataFrame:
    """
    Construye un portafolio mensual con los símbolos dados
    
    Args:
        returns_df: DataFrame con retornos diarios
        start_date: Fecha de inicio del mes
        cols: Símbolos a incluir en el portafolio
    
    Returns:
        DataFrame con retornos del portafolio para el mes
    """
    # Calcula fecha de fin del mes
    end_date = (pd.to_datetime(start_date) + pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
    # Filtra símbolos válidos (que existan en returns_df)
    valid_cols = [c for c in cols if c in returns_df.columns]
    
    # Si no hay símbolos válidos, retorna DataFrame vacío
    if not valid_cols:
        return pd.DataFrame()
    
    # Calcula retorno promedio diario del portafolio para el mes
    temp_df = returns_df[start_date:end_date][valid_cols].mean(axis=1).to_frame('portfolio_returns')
    
    return temp_df

# Función para ensamblar el portafolio completo
def assemble_portfolio_sequential(returns_df: pd.DataFrame, fixed_dates: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Construye el portafolio completo mes a mes
    
    Args:
        returns_df: DataFrame con retornos diarios
        fixed_dates: Diccionario con {fecha: [símbolos]} para cada mes
    
    Returns:
        DataFrame con retornos del portafolio completo
    """
    portfolio_df = pd.DataFrame()  # DataFrame vacío para acumular resultados
    
    # Para cada mes y sus símbolos
    for d, cols in fixed_dates.items():
        # Construye el portafolio del mes y lo concatena
        portfolio_df = pd.concat([portfolio_df, build_monthly_portfolio_sequential(returns_df, d, cols)], axis=0)
    
    return portfolio_df

# Función para obtener retornos del benchmark (QQQ)
def get_benchmark_returns_sequential(start: str = '2021-01-01', end: str = '2023-03-01') -> pd.Series:
    """
    Obtiene retornos diarios del ETF QQQ (benchmark NASDAQ)
    
    Args:
        start: Fecha de inicio en formato 'YYYY-MM-DD'
        end: Fecha de fin en formato 'YYYY-MM-DD'
    
    Returns:
        Serie con retornos diarios del benchmark
    """
    # Descarga datos del QQQ
    qqq_df = yf.download(tickers='QQQ', start=start, end=end, progress=False)
    # Calcula retornos logarítmicos
    return np.log(qqq_df['Close']).diff()

# Función para calcular retornos acumulados
def calculate_cumulative_returns_sequential(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula retornos acumulados a partir de retornos diarios
    
    Args:
        portfolio_df: DataFrame con retornos diarios del portafolio
    
    Returns:
        DataFrame con retornos acumulados
    """
    return np.exp(np.log1p(portfolio_df).cumsum()).sub(1)

# Función principal para ejecutar el pipeline secuencial
def run_pipeline_sequential(criterio: str = "engagement_ratio", path: str = "datasets/sentiment_data.csv") -> pd.DataFrame:
    """
    Ejecuta todo el pipeline de procesamiento de forma secuencial
    
    Args:
        criterio: Criterio para filtrar y rankear (default: 'engagement_ratio')
        path: Ruta al archivo de datos de sentimiento
    
    Returns:
        DataFrame con retornos acumulados del portafolio y benchmark
    """
    # 1. Carga y procesa datos de sentimiento
    sentiment_df = load_sentiment_data_sequential(path)
    
    # 2. Filtra y rankea los datos
    filtered_df = filter_and_rank_sequential(sentiment_df, criterio)
    
    # 3. Organiza los símbolos por fecha
    fixed_dates = get_filtered_dates_sequential(filtered_df)

    # 4. Obtiene todos los símbolos únicos y los valida
    symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
    valid_symbols, _ = validate_symbols_sequential(symbols)
    
    # 5. Descarga precios históricos para símbolos válidos
    prices_df = download_prices_sequential(valid_symbols)
    
    # 6. Calcula retornos diarios
    returns_df = calculate_returns_sequential(prices_df)
    
    # 7. Construye el portafolio completo
    portfolio_df = assemble_portfolio_sequential(returns_df, fixed_dates)
    
    # 8. Obtiene retornos del benchmark (QQQ)
    benchmark_series = get_benchmark_returns_sequential()
    portfolio_df['nasdaq_return'] = benchmark_series
    
    # 9. Calcula retornos acumulados
    cumulative_df = calculate_cumulative_returns_sequential(portfolio_df)

    # 10. Guarda resultados en archivo CSV
    os.makedirs("results", exist_ok=True)
    cumulative_df.to_csv("results/cumulative_returns_sequential.csv")

    return cumulative_df

# Función para ejecutar el pipeline en paralelo con Ray
def run_parallel_pipeline(criterio: str = "engagement_ratio", path: str = "datasets/sentiment_data.csv") -> pd.DataFrame:
    """
    Ejecuta todo el pipeline de procesamiento en paralelo usando Ray
    
    Args:
        criterio: Criterio para filtrar y rankear (default: 'engagement_ratio')
        path: Ruta al archivo de datos de sentimiento
    
    Returns:
        DataFrame con retornos acumulados del portafolio y benchmark
    """
    start_time = time.time()  # Inicia cronómetro
    
    # Inicia Ray para procesamiento paralelo
    ray.init(ignore_reinit_error=True)
    
    # 1. Carga y procesa datos de sentimiento (paralelo)
    sentiment_df = load_sentiment_data(path)
    
    # 2. Filtra y rankea los datos (paralelo)
    filtered_df = filter_and_rank(sentiment_df, criterio)
    
    # 3. Organiza los símbolos por fecha (paralelo)
    fixed_dates = get_filtered_dates(filtered_df)
    
    # 4. Obtiene todos los símbolos únicos
    symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
    
    # 5. Valida símbolos en paralelo
    valid_symbols, _ = validate_symbols_parallel(symbols)
    
    # 6. Descarga precios en paralelo
    prices_df = ray.get(download_prices.remote(valid_symbols))
    
    # 7. Calcula retornos diarios
    returns_df = calculate_returns(prices_df)
    
    # 8. Construye el portafolio completo
    portfolio_df = assemble_portfolio(returns_df, fixed_dates)
    
    # 9. Obtiene retornos del benchmark (QQQ)
    benchmark_series = get_benchmark_returns()
    portfolio_df['nasdaq_return'] = benchmark_series
    
    # 10. Calcula retornos acumulados
    cumulative_df = calculate_cumulative_returns(portfolio_df)
    
    # Mide y muestra tiempo de ejecución
    elapsed_time = time.time() - start_time
    print(f"Tiempo de ejecución paralelo: {elapsed_time:.2f} segundos")
    
    # Guarda resultados en archivo CSV
    os.makedirs("results", exist_ok=True)
    cumulative_df.to_csv("results/cumulative_returns_parallel.csv")
    
    return cumulative_df

# Función principal para comparar ambos métodos
if __name__ == "__main__":
    # Benchmarking del método secuencial
    print("Iniciando procesamiento secuencial de datos...")
    cpu_before_secuencial = measure_cpu_usage()
    start_time = time.time()
    result_secuencial = run_pipeline_sequential()
    secuencial_time = time.time() - start_time
    cpu_after_secuencial = measure_cpu_usage()
    
    print(f"\nRESULTADOS PROCESAMIENTO SECUENCIAL:")
    print(f"- Duración total: {secuencial_time:.2f} segundos")
    print(f"- Consumo de CPU promedio: {cpu_after_secuencial}%")

    # Benchmarking del método paralelo
    print("\nIniciando procesamiento paralelo con Ray...")
    cpu_before_paralelo = measure_cpu_usage()
    start_time = time.time()
    result_paralelo = run_parallel_pipeline()
    paralelo_time = time.time() - start_time
    cpu_after_paralelo = measure_cpu_usage()
    
    print(f"\nRESULTADOS PROCESAMIENTO PARALELO:")
    print(f"- Duración total: {paralelo_time:.2f} segundos")
    print(f"- Consumo de CPU promedio: {cpu_after_paralelo}%")

    # Comparación de resultados
    print("\nCOMPARACIÓN FINAL:")
    print("| Método       | Tiempo (s) | CPU (%) |")
    print("|--------------|------------|---------|")
    print(f"| Secuencial   | {secuencial_time:>10.2f} | {cpu_after_secuencial:>7} |")
    print(f"| Paralelo     | {paralelo_time:>10.2f} | {cpu_after_paralelo:>7} |")

    # Preparación de datos para gráficos
    tiempos = {
        "Secuencial": secuencial_time,
        "Paralelo": paralelo_time
    }

    cpu_usage = {
        "Secuencial": cpu_after_secuencial,
        "Paralelo": cpu_after_paralelo
    }

    # Creación de gráfico comparativo
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Gráfico de barras para tiempos de ejecución
    ax1.bar(tiempos.keys(), tiempos.values(), color='b', alpha=0.6, 
            label="Tiempo (segundos)", width=0.4, align='center')
    ax1.set_ylabel("Tiempo (segundos)", color='b')
    ax1.set_xlabel("Método")

    # Gráfico de línea para uso de CPU
    ax2 = ax1.twinx()
    ax2.plot(cpu_usage.keys(), cpu_usage.values(), color='r', marker='o', 
             label="Uso de CPU (%)", linewidth=2)
    ax2.set_ylabel("Uso de CPU (%)", color='r')

    # Configuración del gráfico
    plt.title("Comparación de Tiempos y Uso de CPU: Secuencial vs Paralelo")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    # Mostrar gráfico
    plt.show()