# Importación de librerías necesarias
from fastapi import APIRouter, Query  # Para crear rutas y manejar parámetros de consulta
from datetime import datetime  # Para manejo de fechas
import numpy as np  # Para cálculos numéricos
import pandas as pd  # Para manipulación de datos
from benchmarking.intraday_compare import benchmark_paralelo, benchmark_secuencial  # Funciones de benchmarking
from ray_task.intraday import (  # Funciones para la estrategia intradía
    cargar_datos_diarios, 
    cargar_datos_intradia,
    generar_senal_diaria,
    generar_senal_intradia,
    calcular_retorno_final
)
from fastapi.responses import FileResponse, JSONResponse  # Respuestas HTTP especializadas
import tempfile  # Para crear archivos temporales

# Creamos un router de FastAPI con prefijo "/intradaily"
router = APIRouter(prefix="/intradaily")

# Variable global para trackear progreso de descarga
download_progress = 0 

# Función para actualizar el progreso de descarga
def update_download_progress(progress: int):
    global download_progress
    download_progress = progress

# Endpoint para ejecutar la estrategia intradía
@router.post("/run-strategy/")
def run_intraday_strategy():
    """
    Ejecuta la estrategia intradía completa:
    1. Carga datos diarios e intradía
    2. Genera señales de trading
    3. Calcula retornos
    4. Guarda resultados en CSV
    """
    # Cargamos datos simulados
    daily_df = cargar_datos_diarios("datasets/simulated_daily_data.csv")
    intraday_df = cargar_datos_intradia("datasets/simulated_5min_data.csv")

    # Generamos señales de trading
    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df = calcular_retorno_final(final_df)
    
    # Guardamos resultados
    final_df.to_csv("output/estrategia_intradia_resultado.csv")
    return {"message": "La Estrategia fue ejecutada y guardada"}

# Endpoint para obtener fechas disponibles
@router.get("/dates")
def available_dates():
    """
    Devuelve las fechas disponibles en los resultados de la estrategia
    """
    # Leemos el archivo de resultados
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=['datetime'])
    # Extraemos fechas únicas y las ordenamos
    fechas = sorted(df['datetime'].dt.date.unique())
    # Convertimos a formato string
    fechas_str = [f.strftime("%Y-%m-%d") for f in fechas]
    return {"dates": fechas_str}

# Endpoint para obtener retornos acumulados
@router.get("/returns", summary="Retornando el acumulado de la estrategia")
def get_cumulative_returns(
    start_date: str = Query(None),  # Parámetro opcional de fecha inicio
    end_date: str = Query(None)    # Parámetro opcional de fecha fin
):
    """
    Calcula retornos acumulados de la estrategia para un rango de fechas
    """
    # Cargamos resultados
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    # Filtramos por fechas si se especificaron
    if start_date:
        df = df[df["date"] >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        df = df[df["date"] <= datetime.strptime(end_date, "%Y-%m-%d").date()]

    # Procesamos retornos
    df["strategy_return"] = df["strategy_return"].fillna(0)
    
    # Agrupamos por día y calculamos acumulado
    daily_df = df.groupby("date")[["strategy_return"]].sum()
    daily_df["cumulative_strategy_return"] = np.exp(np.log1p(daily_df["strategy_return"]).cumsum()) - 1
    
    # Formateamos resultados
    daily_df = daily_df.reset_index()
    daily_df["date"] = daily_df["date"].astype(str)
    daily_df["cumulative_strategy_return"] = daily_df["cumulative_strategy_return"] * 100  # Convertimos a porcentaje

    return daily_df[["date", "cumulative_strategy_return"]].to_dict(orient="records")

# Endpoint para retornos diarios simples
@router.get("/returns/daily", summary="Este es el retorno diario simple (sin acumulado)")
def get_daily_returns(
    start_date: str = Query(None),
    end_date: str = Query(None)):
    """
    Devuelve retornos diarios no acumulados
    """
    # Cargamos y procesamos datos similar al endpoint anterior
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    if start_date:
        df = df[df["date"] >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        df = df[df["date"] <= datetime.strptime(end_date, "%Y-%m-%d").date()]

    # Calculamos retornos diarios
    daily_return_df = df.groupby("date")[["strategy_return"]].sum().reset_index()
    daily_return_df["strategy_return"] = daily_return_df["strategy_return"] * 100  # A porcentaje
    daily_return_df["date"] = daily_return_df["date"].astype(str)

    return daily_return_df.to_dict(orient="records")

# Endpoint para descargar resultados
@router.get("/returns/download", summary="Descargar CSV del retorno actual")
def download_returns_csv(
    start_date: str = Query(None),
    end_date: str = Query(None),
    tipo: str = Query("acumulado")  # Tipo de retorno ('acumulado' o otro)
):
    """
    Permite descargar los resultados como archivo CSV
    """
    # Cargamos y filtramos datos
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    if start_date:
        df = df[df["date"] >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        df = df[df["date"] <= datetime.strptime(end_date, "%Y-%m-%d").date()]

    # Procesamos retornos
    df["strategy_return"] = df["strategy_return"].fillna(0)
    result_df = df.groupby("date")[["strategy_return"]].sum()

    # Calculamos acumulado si se especificó
    if tipo == "acumulado":
        result_df["cumulative_strategy_return"] = np.exp(np.log1p(result_df["strategy_return"]).cumsum()) - 1
        result_df = result_df[["cumulative_strategy_return"]]
    else:
        result_df = result_df[["strategy_return"]]

    # Creamos archivo temporal CSV
    result_df = result_df.reset_index()
    result_df["date"] = result_df["date"].astype(str)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="") as tmp:
        result_df.to_csv(tmp.name, index=False)
        return FileResponse(tmp.name, filename=f"retornos_{tipo}.csv", media_type="text/csv")

# Endpoint para obtener progreso de descarga
@router.get("/download/progress", summary="Obtener el progreso de la descarga de datos")
def get_download_progress():
    """
    Devuelve el progreso actual de las descargas
    """
    return {"progress": download_progress}

# Endpoint para comparar métodos secuencial vs paralelo
@router.get("/compare", summary="Comparación de rendimiento: Secuencial vs Paralelo")
def benchmark():
    """
    Ejecuta y compara el rendimiento de las versiones secuencial y paralela
    """
    # Paths a los datos simulados
    path_diarios = "datasets/simulated_daily_data.csv"
    path_intraday = "datasets/simulated_5min_data.csv"
    
    # Ejecutamos benchmarks actualizando progreso
    update_download_progress(50)  
    print("rendimiento secuencial")
    result_secuencial, secuencial_time, cpu_secuencial = benchmark_secuencial(path_diarios, path_intraday)
   
    update_download_progress(75)  
    print("rendimiento paralelo")
    result_paralelo, paralelo_time, cpu_paralelo = benchmark_paralelo(path_diarios, path_intraday)
    
    update_download_progress(100)  
    print("Comparación completada.")
    
    # Preparamos datos de comparación
    comparison_data = {
        "secuencial": {
            "tiempo": secuencial_time,  # Tiempo ejecución secuencial
            "cpu": cpu_secuencial      # Uso de CPU secuencial
        },
        "paralelo": {
            "tiempo": paralelo_time,    # Tiempo ejecución paralelo
            "cpu": cpu_paralelo        # Uso de CPU paralelo
        }
    }

    return JSONResponse(content=comparison_data)  # Devolvemos como JSON