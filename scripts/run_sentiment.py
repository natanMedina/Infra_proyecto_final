"""
Estrategia cuantitativa que utiliza datos de sentimiento de Twitter para:
1. Rankear activos mensualmente según métricas de sentimiento.
2. Construir un portafolio teórico y compararlo contra el benchmark (NASDAQ QQQ).
3. Visualizar retornos acumulados.
Utiliza procesamiento paralelo con Ray para optimizar validación de símbolos y descarga de precios.
"""

import ray
import pandas as pd
import matplotlib.pyplot as plt
from ray_task.sentiment import (
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

# Inicializar Ray para procesamiento distribuido
ray.init()

# ================= CONFIGURACIÓN =================
DATA_PATH = "datasets/sentiment_data.csv"
OUTPUT_PATH = "output/cumulative_returns.csv"

# ================= ETAPA 1: PREPARACIÓN DE DATOS =================
print("[1/5] Cargando y procesando datos de sentimiento...")
sentiment_df = load_sentiment_data(DATA_PATH)

print("[2/5] Generando ranking mensual de activos...")
filtered_df = filter_and_rank(sentiment_df)
rebalance_dates = get_filtered_dates(filtered_df)

# ================= ETAPA 2: VALIDACIÓN DE SÍMBOLOS =================
symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
print(f"[3/5] Validando {len(symbols)} tickers en paralelo...")
valid_symbols, failed_symbols = validate_symbols_parallel(symbols)

print(f"  → Tickers válidos: {len(valid_symbols)}")
print(f"  → Tickers descartados: {len(failed_symbols)}")

# ================= ETAPA 3: CONSTRUCCIÓN DE PORTAFOLIO =================
print("[4/5] Descargando precios y calculando retornos...")
prices_df = ray.get(download_prices.remote(valid_symbols))
returns_df = calculate_returns(prices_df)

print("Construyendo portafolio teórico...")
portfolio_df = assemble_portfolio(returns_df, rebalance_dates)

# ================= ETAPA 4: BENCHMARK & ANÁLISIS =================
print("[5/5] Comparando contra benchmark (NASDAQ QQQ)...")
benchmark_returns = get_benchmark_returns()
portfolio_df['benchmark_return'] = benchmark_returns

cumulative_returns = calculate_cumulative_returns(portfolio_df)
cumulative_returns.to_csv(OUTPUT_PATH, index=False)

# ================= VISUALIZACIÓN =================
print("Generando gráfico comparativo...")
df = pd.read_csv(OUTPUT_PATH, parse_dates=["Date"])
df.set_index("Date", inplace=True)

plt.figure(figsize=(12, 6))
plt.plot(
    df["portfolio_returns"], 
    label="Estrategia (Sentimiento Twitter)", 
    color="#2c7be5",
    linewidth=2
)
plt.plot(
    df["benchmark_return"], 
    label="NASDAQ QQQ", 
    linestyle="--", 
    color="#767676"
)
plt.title("Retornos Acumulados: Estrategia vs Benchmark", pad=20)
plt.xlabel("Fecha", labelpad=10)
plt.ylabel("Retorno (%)", labelpad=10)
plt.legend(frameon=False)
plt.grid(axis="y", linestyle=":", alpha=0.7)
plt.tight_layout()

plt.savefig("output/returns_comparison.png", dpi=300)
print(f"Resultados guardados en: {OUTPUT_PATH} y output/returns_comparison.png")