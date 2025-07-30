import time
from matplotlib import pyplot as plt
import ray
import pandas as pd
import numpy as np
import psutil
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from arch import arch_model

from ray_task.intraday import (
    cargar_datos_intradia,
    predecir_varianza_garch,
    generar_senal_diaria,
    generar_senal_intradia,
    calcular_retorno_final,
    cargar_datos_diarios
)

# Función para medir el uso promedio del CPU durante un periodo dado
def measure_cpu_usage(interval=1, duration=3):
    cpu_readings = [psutil.cpu_percent(interval=interval) for _ in range(duration)]
    return np.mean(cpu_readings)

# Carga datos diarios desde un archivo CSV y calcula el log-retorno
def cargar_datos_secuencial(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df['log_ret'] = np.log(df['Adj Close']).diff()
    return df

# Genera señal diaria basada en un modelo GARCH sobre ventanas móviles
def generar_senal_diaria_secuencial(df):
    df = df.copy()
    df['variance'] = df['log_ret'].rolling(180).var()
    df = df['2020-01-01':].copy()

    ventanas = [df['log_ret'].iloc[i-180:i] for i in range(180, len(df)+1)]
    results = []
    for ventana in ventanas:
        model = arch_model(y=ventana, p=1, q=3)
        fitted = model.fit(update_freq=5, disp='off')
        results.append(fitted.forecast(horizon=1).variance.iloc[-1, 0])

    df.loc[df.index[179:], 'predictions'] = results
    df['prediction_premium'] = (df['predictions'] - df['variance']) / df['variance']
    df['premium_std'] = df['prediction_premium'].rolling(180).std()
    df['signal_daily'] = df.apply(
        lambda x: 1 if x['prediction_premium'] > 1.5 * x['premium_std'] else 
                  (-1 if x['prediction_premium'] < -1.5 * x['premium_std'] else np.nan), axis=1)
    df['signal_daily'] = df['signal_daily'].shift()
    return df

# Genera señales intradía combinando RSI, Bandas de Bollinger y señales diarias
def generar_senal_intradia_secuencial(intraday_df, senales_diarias):
    df = intraday_df.reset_index()\
            .merge(senales_diarias[['signal_daily']].reset_index(), left_on='date', right_on='Date')\
            .set_index('datetime')
    df = df.drop(['date', 'Date'], axis=1)

    # Indicadores técnicos
    rsi = RSIIndicator(close=df['close'], window=20)
    df['rsi'] = rsi.rsi()

    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['lband'] = bb.bollinger_lband()
    df['uband'] = bb.bollinger_hband()

    # Reglas para señal intradía basada en RSI y Bandas de Bollinger
    def signal(row):
        if row['rsi'] > 70 and row['close'] > row['uband']:
            return 1
        elif row['rsi'] < 30 and row['close'] < row['lband']:
            return -1
        else:
            return np.nan

    df['signal_intraday'] = df.apply(signal, axis=1)

    # Combina señales intradía y diarias
    def combinacion(row):
        if row['signal_daily'] == 1 and row['signal_intraday'] == 1:
            return -1
        elif row['signal_daily'] == -1 and row['signal_intraday'] == -1:
            return 1
        else:
            return np.nan

    df['return_sign'] = df.apply(combinacion, axis=1)
    df['return_sign'] = df.groupby(pd.Grouper(freq='D'))['return_sign'].transform(lambda x: x.ffill())
    return df

# Calcula el retorno acumulado de la estrategia
def calcular_retorno_final_secuencial(df):
    df = df.copy()
    df['return'] = df['close'].pct_change()
    df['forward_return'] = df['return'].shift(-1)
    df['strategy_return'] = df['forward_return'] * df['return_sign']
    df['strategy_return'] = df['strategy_return'].fillna(0)
    df['cumulative_strategy_return'] = np.exp(np.log1p(df['strategy_return']).cumsum()) - 1
    return df

# Ejecuta todo el pipeline de forma secuencial
def run_pipeline_secuencial(path_diarios, path_intraday):
    df_diarios = cargar_datos_secuencial(path_diarios)
    df_intraday = cargar_datos_intradia(path_intraday)
    df_senales_diarias = generar_senal_diaria_secuencial(df_diarios)
    df_senales_intraday = generar_senal_intradia_secuencial(df_intraday, df_senales_diarias)
    df_retorno = calcular_retorno_final_secuencial(df_senales_intraday)
    return df_retorno

# Benchmark del pipeline secuencial (tiempo y uso de CPU)
def benchmark_secuencial(path_diarios, path_intraday):
    print("Ejecutando pipeline secuencial...")
    print("Evaluando uso de CPU antes del procesamiento...")
    cpu_before = measure_cpu_usage()  
    print(f"Uso de CPU inicial: {cpu_before:.2f}%")
    
    start_time = time.time()
    result_secuencial = run_pipeline_secuencial(path_diarios, path_intraday)
    secuencial_time = time.time() - start_time
    
    print("Evaluando uso de CPU después del procesamiento...")
    cpu_after = measure_cpu_usage()
    print(f"Uso de CPU final: {cpu_after:.2f}%")
    
    print(f"Tiempo total del pipeline secuencial: {secuencial_time:.2f} segundos")
    print(f"Variación del uso de CPU: {cpu_after - cpu_before:.2f}%")
    
    return result_secuencial, secuencial_time, cpu_after

# Ejecuta el pipeline usando Ray en paralelo
def run_parallel_pipeline(path_diarios, path_intraday):
    ray.init(ignore_reinit_error=True)
    
    df_diarios = cargar_datos_diarios(path_diarios)  
    df_intraday = cargar_datos_intradia(path_intraday)
    df_senales_diarias = generar_senal_diaria(df_diarios)
    df_senales_intraday = generar_senal_intradia(df_intraday, df_senales_diarias)
    df_retorno = calcular_retorno_final(df_senales_intraday)
    return df_retorno

# Benchmark del pipeline paralelo (tiempo y uso de CPU)
def benchmark_paralelo(path_diarios, path_intraday):
    print("Ejecutando pipeline en paralelo con Ray...")
    print("Evaluando uso de CPU antes del procesamiento paralelo...")
    cpu_before = measure_cpu_usage() 
    print(f"Uso de CPU inicial: {cpu_before:.2f}%")
    
    start_time = time.time()
    result_paralelo = run_parallel_pipeline(path_diarios, path_intraday)
    paralelo_time = time.time() - start_time
    
    print("Evaluando uso de CPU después del procesamiento paralelo...")
    cpu_after = measure_cpu_usage()  
    print(f"Uso de CPU final: {cpu_after:.2f}%")
    
    print(f"Tiempo total del pipeline paralelo: {paralelo_time:.2f} segundos")
    print(f"Variación del uso de CPU: {cpu_after - cpu_before:.2f}%")
    
    return result_paralelo, paralelo_time, cpu_after

# Punto de entrada principal para ejecutar los benchmarks
if __name__ == "__main__":
    path_diarios = "datasets/simulated_daily_data.csv"
    path_intraday = "datasets/simulated_5min_data.csv"
    
    # Benchmark secuencial
    result_secuencial, secuencial_time, cpu_secuencial = benchmark_secuencial(path_diarios, path_intraday)

    # Benchmark paralelo
    result_paralelo, paralelo_time, cpu_paralelo = benchmark_paralelo(path_diarios, path_intraday)

     # Comparación de resultados
    print("\nResultados comparativos entre ejecución secuencial y paralela:")
    print(f"Tiempo (secuencial): {secuencial_time:.2f} segundos")
    print(f"Uso de CPU (secuencial): {cpu_secuencial:.2f}%")
    print(f"Tiempo (paralelo): {paralelo_time:.2f} segundos")
    print(f"Uso de CPU (paralelo): {cpu_paralelo:.2f}%")

    # Visualización comparativa
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.bar(["Secuencial", "Paralelo"], [secuencial_time, paralelo_time], color='blue', alpha=0.6, width=0.4)
    ax1.set_ylabel("Tiempo (segundos)", color='blue')
    ax1.set_xlabel("Método")

    ax2 = ax1.twinx()
    ax2.plot(["Secuencial", "Paralelo"], [cpu_secuencial, cpu_paralelo], color='red', marker='o', linewidth=2)
    ax2.set_ylabel("Uso de CPU (%)", color='red')

    plt.title("Comparación de Tiempos de Ejecución y Uso de CPU: Secuencial vs Paralelo")
    ax1.legend(["Tiempo de Ejecución"], loc="upper left")
    ax2.legend(["Uso de CPU"], loc="upper right")
    plt.show()