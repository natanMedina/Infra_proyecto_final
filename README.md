# 📊 Portfolio Analytics Dashboard - Proyecto Final de Infraestructuras

## 🎯 Contexto del Proyecto

Este proyecto implementa un **sistema de análisis de portafolios de inversión** que demuestra la aplicación práctica de **computación paralela y distribuida** en el análisis financiero. El objetivo principal es optimizar el procesamiento de grandes volúmenes de datos financieros utilizando el framework Ray.

### Estrategias Implementadas

1. **Análisis de Sentimiento Social**: Utiliza datos de redes sociales (Twitter) para identificar activos con alto engagement y construir portafolios basados en sentimiento del mercado.

2. **Trading Intradía**: Implementa estrategias de trading basadas en modelos GARCH para predicción de volatilidad e indicadores técnicos (RSI, Bandas de Bollinger) para señales de entrada/salida.

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

**Backend (Procesamiento y API)**

- **Ray 2.31.0**: Framework principal para computación distribuida y paralela
- **FastAPI 0.110.0**: Framework web para API REST
- **Ray Serve**: Para servir modelos y aplicaciones en producción
- **Pandas/NumPy**: Manipulación y análisis de datos
- **yfinance**: Descarga de datos financieros
- **scikit-learn**: Modelos de machine learning
- **arch**: Modelos GARCH para análisis de volatilidad
- **ta**: Indicadores técnicos

**Frontend (Dashboard)**

- **React 19**: Framework de interfaz de usuario
- **Vite**: Build tool y servidor de desarrollo
- **Tailwind CSS**: Framework de estilos
- **Recharts**: Gráficos interactivos
- **Axios**: Cliente HTTP para comunicación con API

**Infraestructura**

- **Docker**: Containerización de servicios
- **Docker Compose**: Orquestación de contenedores

## 🔄 Estrategias de Paralelización

### 1. Análisis de Sentimiento (`ray_task/sentiment.py`)

**Funciones Paralelas Implementadas:**

- **Validación paralela de símbolos**: Verificación simultánea de múltiples activos financieros
- **Descarga paralela de precios**: Obtención concurrente de datos históricos
- **Construcción paralela de portafolios**: Cálculo simultáneo de retornos por mes

**Metodología:**

```python
@ray.remote
def validate_symbol(symbol: str) -> Tuple[str, bool]:
    # Validación paralela de símbolos financieros

@ray.remote
def download_prices(symbols: List[str]) -> pd.DataFrame:
    # Descarga paralela de precios históricos
```

**Pipeline de Procesamiento:**

1. Carga de datos de sentimiento social
2. Filtrado por engagement (likes > 20, comentarios > 10)
3. Ranking mensual de top 5 activos
4. Validación paralela de símbolos
5. Descarga paralela de precios históricos
6. Construcción de portafolio con rebalanceo mensual
7. Cálculo de retornos acumulados vs benchmark (S&P 500)

### 2. Trading Intradía (`ray_task/intraday.py`)

**Funciones Paralelas Implementadas:**

- **Predicción GARCH paralela**: Ajuste simultáneo de modelos GARCH para diferentes ventanas temporales
- **Procesamiento de señales**: Cálculo paralelo de indicadores técnicos

**Metodología:**

```python
@ray.remote
def predecir_varianza_garch(x):
    # Predicción paralela de varianza usando modelos GARCH(1,3)
```

**Pipeline de Procesamiento:**

1. Carga de datos diarios e intradía
2. Cálculo de retornos logarítmicos
3. Predicción paralela de varianza usando modelos GARCH
4. Generación de señales diarias basadas en desviaciones de volatilidad
5. Cálculo de indicadores técnicos (RSI, Bandas de Bollinger)
6. Combinación de señales diarias e intradía
7. Cálculo de retornos finales de la estrategia

### 3. Benchmarking (`benchmarking/`)

**Comparación Implementada:**

- **Secuencial vs Paralelo**: Medición de performance entre implementaciones
- **Monitoreo de recursos**: Seguimiento de uso de CPU y memoria
- **Métricas de rendimiento**: Tiempo de ejecución, throughput, eficiencia

## 📊 Metodología de Análisis

### Datos Utilizados

**Análisis de Sentimiento:**

- **sentiment_data.csv**: Datos de sentimiento social con métricas de engagement
- **Período**: 2021-01-01 a 2023-03-01
- **Métricas**: twitterLikes, twitterComments, engagement_ratio

**Trading Intradía:**

- **simulated_daily_data.csv**: Datos diarios simulados
- **simulated_5min_data.csv**: Datos intradía simulados (5 minutos)
- **Ventana GARCH**: 180 días para predicción de volatilidad

### Algoritmos y Modelos

**Modelos GARCH:**

- **Configuración**: GARCH(1,3) - 1 término ARCH, 3 términos GARCH
- **Objetivo**: Predicción de varianza futura para detección de volatilidad anómala
- **Umbral**: 1.5 desviaciones estándar para generación de señales

**Indicadores Técnicos:**

- **RSI**: Relative Strength Index para identificación de sobrecompra/sobreventa
- **Bandas de Bollinger**: Bandas de volatilidad para señales de entrada/salida

**Métricas de Sentimiento:**

- **Engagement Ratio**: Comentarios/Likes como proxy de engagement
- **Filtros**: Mínimo 20 likes y 10 comentarios por tuit
- **Ranking**: Top 5 activos por mes según criterio seleccionado

## 📈 Métricas de Performance

### Métricas Computacionales

- **Tiempo de ejecución**: Comparación secuencial vs paralelo
- **Uso de CPU**: Monitoreo de utilización de recursos
- **Throughput**: Capacidad de procesamiento de datos
- **Escalabilidad**: Comportamiento con volúmenes crecientes de datos

### Métricas Financieras

- **Retornos acumulados**: Comparación con benchmark
- **Sharpe ratio**: Retorno ajustado por riesgo
- **Drawdown**: Pérdida máxima desde pico
- **Volatilidad**: Desviación estándar de retornos

### Archivos de Resultados

- `results/cumulative_returns_parallel.csv`: Retornos con procesamiento paralelo
- `results/cumulative_returns_sequential.csv`: Retornos con procesamiento secuencial
- `output/`: Gráficos y visualizaciones de resultados

## 🔬 Validación y Testing

### Estrategias de Validación

- **Consistencia**: Comparación entre ejecuciones secuenciales y paralelas
- **Precisión**: Validación de cálculos financieros
- **Performance**: Monitoreo de uso de recursos

### Scripts de Benchmarking

- `benchmarking/sentiment_compare.py`: Comparación de análisis de sentimiento
- `benchmarking/intraday_compare.py`: Comparación de trading intradía

## 📁 Estructura del Proyecto

```
Infra_proyecto_final/
├── api/                          # Backend API
│   ├── main.py                   # Punto de entrada principal con Ray Serve
│   ├── sentiment/                # Endpoints de análisis de sentimiento
│   └── intraday/                 # Endpoints de trading intradía
├── ray_task/                     # Lógica de procesamiento paralelo
│   ├── sentiment.py              # Pipeline de análisis de sentimiento
│   └── intraday.py               # Pipeline de trading intradía
├── benchmarking/                 # Comparación de performance
│   ├── sentiment_compare.py      # Benchmarking análisis de sentimiento
│   └── intraday_compare.py       # Benchmarking trading intradía
├── Client/                       # Frontend React
├── datasets/                     # Datos de entrada
├── scripts/                      # Scripts de ejecución
├── results/                      # Resultados de benchmarking
└── output/                       # Salidas de análisis
```

## 🎯 Objetivos de Investigación

### Preguntas de Investigación

1. **¿Qué mejora en performance se obtiene con computación paralela vs secuencial?**
2. **¿Cómo escalan las estrategias de paralelización con volúmenes crecientes de datos?**
3. **¿Qué impacto tiene la paralelización en la precisión de los modelos financieros?**
4. **¿Cuáles son las limitaciones y trade-offs de cada estrategia de paralelización?**

### Hipótesis

- La computación paralela reduce significativamente el tiempo de procesamiento
- El framework Ray permite escalabilidad lineal hasta cierto punto
- La precisión de los modelos se mantiene con procesamiento paralelo
- Los beneficios de paralelización varían según el tipo de tarea

## 📊 Resultados Esperados

### Métricas Cuantitativas

- **Reducción de tiempo**: Esperado 50-70% menos tiempo de procesamiento
- **Escalabilidad**: Capacidad de procesar 2-4x más datos sin degradación lineal
- **Eficiencia de recursos**: Mejor utilización de CPU multi-core

### Análisis Comparativo

- **Secuencial vs Paralelo**: Medición directa de mejora en performance
- **Diferentes estrategias**: Comparación entre análisis de sentimiento y trading intradía
- **Volúmenes de datos**: Análisis de escalabilidad con datasets crecientes

---

**Nota**: Este proyecto está diseñado como demostración de computación paralela y distribuida aplicada al análisis financiero. Los resultados no deben considerarse como consejos de inversión.
