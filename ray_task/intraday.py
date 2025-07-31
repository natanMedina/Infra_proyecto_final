# Librerías para manipulación de datos, series temporales y análisis técnico
import pandas as pd
import numpy as np
from arch import arch_model  # Para modelos GARCH
from ta.momentum import RSIIndicator  # Indicador técnico RSI
from ta.volatility import BollingerBands  # Bandas de Bollinger
import os
import ray  # Librería para computación paralela/distribuida

# -----------------------------
# CARGA DE DATOS
# -----------------------------

def cargar_datos_diarios(path):
    """
    Carga un archivo CSV con datos diarios, elimina columnas 'Unnamed',
    convierte la columna 'Date' a índice de tipo datetime y calcula el retorno logarítmico.
    """
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df['log_ret'] = np.log(df['Adj Close']).diff()
    return df

def cargar_datos_intradia(path):
    """
    Carga un archivo CSV con datos intradía, elimina columnas 'Unnamed',
    convierte la columna 'datetime' a índice de tipo datetime y extrae la fecha.
    """
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    df['date'] = pd.to_datetime(df.index.date)
    return df

# -----------------------------
# MODELO GARCH Y SEÑALES DIARIAS
# -----------------------------

@ray.remote
def predecir_varianza_garch(x):
    """
    Ajusta un modelo GARCH(1,3) a la serie temporal `x` y devuelve
    la varianza pronosticada para el siguiente periodo.
    Esta función es ejecutada en paralelo usando Ray.
    """
    model = arch_model(y=x, p=1, q=3)
    fitted = model.fit(update_freq=5, disp='off')
    return fitted.forecast(horizon=1).variance.iloc[-1, 0]

def generar_senal_diaria(df):
    """
    Genera señales de trading diarias usando un modelo GARCH para predecir varianza futura.
    Se compara la varianza pronosticada con la varianza histórica y se genera una señal si hay desviaciones fuertes.
    """
    df = df.copy()
    
    # Varianza histórica sobre ventana de 180 días
    df['variance'] = df['log_ret'].rolling(180).var()
    df = df['2020-01-01':].copy()  # Filtramos fechas desde 2020

    # Creamos ventanas de 180 días para cada día
    ventanas = [df['log_ret'].iloc[i-180:i] for i in range(180, len(df)+1)]

    # Ejecutamos las predicciones GARCH en paralelo
    futures = [predecir_varianza_garch.remote(v) for v in ventanas]
    resultados = ray.get(futures)

    # Guardamos los resultados en el dataframe
    df.loc[df.index[179:], 'predictions'] = resultados
    df['prediction_premium'] = (df['predictions'] - df['variance']) / df['variance']
    df['premium_std'] = df['prediction_premium'].rolling(180).std()

    # Generamos señal diaria con umbral más bajo (1.0 en lugar de 1.5)
    df['signal_daily'] = df.apply(
        lambda x: 1 if x['prediction_premium'] > 1.0 * x['premium_std'] else 
                  (-1 if x['prediction_premium'] < -1.0 * x['premium_std'] else np.nan),
        axis=1
    )
    df['signal_daily'] = df['signal_daily'].shift()  # Shift para evitar lookahead bias
    return df

# -----------------------------
# SEÑALES INTRADÍA (RSI + BOLLINGER BANDS)
# -----------------------------

def generar_senal_intradia(intraday_df, senales_diarias):
    """
    Genera señales intradía basadas en indicadores técnicos (RSI y Bandas de Bollinger)
    combinadas con la señal diaria GARCH. La señal combinada se usa para tomar decisiones de inversión.
    """
    # Unimos datos intradía con señal diaria
    df = intraday_df.reset_index()\
            .merge(senales_diarias[['signal_daily']].reset_index(), left_on='date', right_on='Date')\
            .set_index('datetime')
    df = df.drop(['date', 'Date'], axis=1)

    # Calculamos RSI
    rsi = RSIIndicator(close=df['close'], window=20)
    df['rsi'] = rsi.rsi()

    # Calculamos Bandas de Bollinger
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['lband'] = bb.bollinger_lband()
    df['uband'] = bb.bollinger_hband()

    # Señal intradía con condiciones menos restrictivas
    def signal(row):
        # Condiciones más flexibles para generar más señales
        if row['rsi'] > 65 or row['close'] > row['uband']:
            return 1  # Sobrecompra: señal de venta
        elif row['rsi'] < 35 or row['close'] < row['lband']:
            return -1  # Sobreventa: señal de compra
        else:
            return np.nan

    df['signal_intraday'] = df.apply(signal, axis=1)

    # Combinación más flexible con señal diaria
    def combinacion(row):
        # Si hay señal diaria, la usamos directamente
        if pd.notna(row['signal_daily']):
            return -row['signal_daily']  # Estrategia contraria
        # Si no hay señal diaria pero hay señal intradía, la usamos
        elif pd.notna(row['signal_intraday']):
            return -row['signal_intraday']  # Estrategia contraria
        else:
            return np.nan

    df['return_sign'] = df.apply(combinacion, axis=1)

    # Propagamos la señal durante el día (forward-fill por día)
    df['return_sign'] = df.groupby(pd.Grouper(freq='D'))['return_sign'].transform(lambda x: x.ffill())
    return df

# -----------------------------
# CÁLCULO DE RETORNO ESTRATÉGICO
# -----------------------------

def calcular_retorno_final(df):
    """
    Calcula los retornos de la estrategia:
    - Retorno diario
    - Retorno adelantado (forward)
    - Retorno de estrategia basada en señales
    - Retorno acumulado exponencial
    """
    df = df.copy()
    df['return'] = df['close'].pct_change()
    df['forward_return'] = df['return'].shift(-1)
    df['strategy_return'] = df['forward_return'] * df['return_sign']
    df['strategy_return'] = df['strategy_return'].fillna(0)

    # Retorno acumulado compuesto
    df['cumulative_strategy_return'] = np.exp(np.log1p(df['strategy_return']).cumsum()) - 1
    return df