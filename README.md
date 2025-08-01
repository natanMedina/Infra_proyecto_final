# proyecto-final-infraesttructuras

# Portfolio Analytics Dashboard

Esta es una aplicación web para análisis de estrategias de inversión basadas en sentimiento del mercado y datos intradía.

### Prerrequisitos
- Python 3.10.0
- Node.js 16+ (para el frontend)
- Git

## Instalación y Ejecución
1. **Clonar repositorio**:
https://github.com/natanMedina/Infra_proyecto_final.git

2. **Verificar que tienes python 3.10:**:
python --version
deberia devolver python 3.10 (no funciona para versiones mas actualizadas)

3. **Instalar dependencias**:
Verificar que estés en la carpeta que contiene "requirements.txt"
pip install -r requirements.txt

4. **Iniciar servidor API**:
python -m api.main

5. **Arrancar con Docker**:
Desde la raiz del proyecto ejecutar:
docker-compose build

Luego
docker-compose up

6. **Acceder a la pagina web**:
Visita http://localhost:5173/ para usar la web.

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
