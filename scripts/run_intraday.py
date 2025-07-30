"""
Script principal para la ejecución de una estrategia de trading que combina:
- Análisis diario (modelo GARCH para volatilidad).
- Análisis intradía (RSI + Bandas de Bollinger para señales de corto plazo).
Utiliza el framework Ray para procesamiento paralelizado.
"""

import ray
from ray_task.intraday import (
    cargar_datos_diarios,
    cargar_datos_intradia,
    generar_senal_diaria,
    generar_senal_intradia,
    calcular_retorno_final
)

# Inicialización de Ray para computación distribuida
ray.init()

# ================ CONFIGURACIÓN DE DATOS ================
RUTA_DATOS_DIARIOS = "datasets/simulated_daily_data.csv"
RUTA_DATOS_INTRADIA = "datasets/simulated_5min_data.csv"

# ================ ETAPA 1: CARGA DE DATOS ================
print("[1/4] Cargando datos históricos diarios e intradía...")
daily_df = cargar_datos_diarios(RUTA_DATOS_DIARIOS)
intraday_df = cargar_datos_intradia(RUTA_DATOS_INTRADIA)

# ================ ETAPA 2: GENERACIÓN DE SEÑALES ================
print("[2/4] Procesando señales diarias (modelo GARCH)...")
daily_df = generar_senal_diaria(daily_df)

print("[3/4] Generando señales intradía (RSI + Bandas de Bollinger)...")
final_df = generar_senal_intradia(intraday_df, daily_df)

# ================ ETAPA 3: EVALUACIÓN ================
print("[4/4] Calculando retornos acumulados de la estrategia...")
final_df = calcular_retorno_final(final_df)

# ================ EXPORTACIÓN ================
RUTA_RESULTADOS = "output/estrategia_intradia_resultado.csv"
print(f"Proceso completado. Resultados guardados en: {RUTA_RESULTADOS}")
final_df.to_csv(RUTA_RESULTADOS, index=False)