# Importación de bibliotecas necesarias
import time  # Para medición de tiempos
from fastapi import APIRouter  # Para creación de rutas API
from fastapi.responses import FileResponse, JSONResponse  # Tipos de respuestas HTTP
import numpy as np  # Para cálculos numéricos
import psutil  # Para monitoreo de CPU
import ray  # Para procesamiento paralelo
from api.sentiment.portfolio import get_cumulative_returns  # Función para obtener retornos acumulados
from api.sentiment.plot import generate_plot  # Función para generar gráficos
from fastapi import Query  # Para parámetros de consulta
from datetime import date  # Para manejo de fechas
import pandas as pd  # Para manipulación de datos
from fastapi.responses import StreamingResponse  # Para streaming de respuestas
import io  # Para manejo de buffers
from pydantic import BaseModel  # Para validación de datos
from ray_task.sentiment import run_pipeline  # Pipeline principal
from ray_task.sentiment import ProgressTracker  # Seguimiento de progreso
from benchmarking.sentiment_compare import run_pipeline_sequential, run_parallel_pipeline  # Funciones de comparación

# Modelo Pydantic para validar entrada de recálculo
class RecalcInput(BaseModel):
    criterio: str  # Criterio para el recálculo

# Creamos el router con prefijo "/sentiment"
router = APIRouter(prefix="/sentiment")

# Función para medir uso promedio de CPU
def measure_cpu_usage(interval=1, duration=3):
    """
    Mide el uso promedio de CPU durante un período.
    
    Args:
        interval: Intervalo entre mediciones en segundos
        duration: Número de mediciones a realizar
    
    Returns:
        Promedio de uso de CPU
    """
    cpu_readings = [psutil.cpu_percent(interval=interval) for _ in range(duration)]
    return np.mean(cpu_readings)

# Variable global para trackear progreso de descarga
download_progress = 0

def update_download_progress(progress: int):
    """Actualiza el progreso global de descarga"""
    global download_progress
    download_progress = progress

# Endpoint para obtener retornos acumulados
@router.get("/returns", summary="Obtener retornos acumulados")
def get_returns():
    """
    Obtiene todos los retornos acumulados del portafolio.
    
    Returns:
        JSON con los retornos acumulados por fecha
    """
    df = get_cumulative_returns()
    df["Date"] = df["Date"].astype(str)  # Convertimos fechas a string
    return JSONResponse(content=df.to_dict(orient="records"))

# Endpoint para obtener gráfico de retornos
@router.get("/plot", summary="Gráfico de retornos acumulados")
def get_plot():
    """
    Genera y devuelve un gráfico de los retornos acumulados.
    
    Returns:
        Imagen PNG del gráfico
    """
    plot_path = generate_plot()
    return FileResponse(plot_path, media_type="image/png")

# Endpoint para retornos filtrados por fecha
@router.get("/returns/filter", summary="Retornos por rango de fechas")
def get_filtered_returns(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    """
    Obtiene retornos acumulados dentro de un rango de fechas.
    
    Args:
        start_date: Fecha inicial del rango
        end_date: Fecha final del rango
    
    Returns:
        JSON con retornos filtrados
    """
    df = get_cumulative_returns()
    # Filtramos por rango de fechas
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    df["Date"] = df["Date"].astype(str)
    return JSONResponse(content=df.to_dict(orient="records"))

# Endpoint para estadísticas del portafolio
@router.get("/returns/stats", summary="Estadísticas del portafolio y Nasdaq")
def get_return_stats():
    """
    Calcula estadísticas clave del portafolio y benchmark.
    
    Returns:
        JSON con medias y desviaciones estándar
    """
    df = get_cumulative_returns()
    stats = {
        "portfolio_mean": df["portfolio_returns"].mean(),  # Media del portafolio
        "portfolio_std": df["portfolio_returns"].std(),   # Desviación estándar
        "nasdaq_mean": df["nasdaq_return"].mean(),        # Media del NASDAQ
        "nasdaq_std": df["nasdaq_return"].std()          # Desviación NASDAQ
    }
    return JSONResponse(content=stats)

# Endpoint para obtener fechas disponibles
@router.get("/returns/dates", summary="Fechas disponibles en los retornos")
def get_dates():
    """
    Obtiene la lista de fechas con datos disponibles.
    
    Returns:
        JSON con lista de fechas en formato YYYY-MM-DD
    """
    df = get_cumulative_returns()
    dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()
    return JSONResponse(content={"dates": dates})

# Endpoint para descargar CSV filtrado
@router.get("/returns/filter/csv", summary="Descargar retornos filtrados por fecha en CSV")
def download_filtered_csv(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
    ):
    """
    Genera y descarga un CSV con retornos filtrados por fecha.
    
    Args:
        start_date: Fecha inicial del rango
        end_date: Fecha final del rango
    
    Returns:
        Archivo CSV para descargar
    """
    df = get_cumulative_returns()
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    df["Date"] = df["Date"].astype(str)

    # Creamos buffer en memoria para el CSV
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Devolvemos como streaming response
    return StreamingResponse(buffer, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename=retornos_{start_date}a{end_date}.csv"
    })

# Actor Ray para trackear progreso
progress_actor = ProgressTracker.remote() 

# Endpoint para recalcular portafolio
@router.post("/recalculate", summary="Recalcular portafolio con criterio dinámico")
def recalculate_portfolio(body: RecalcInput):
    """
    Recalcula el portafolio usando un nuevo criterio.
    
    Args:
        body: Contiene el criterio para el recálculo
    
    Returns:
        JSON con los nuevos retornos calculados
    """
    df = run_pipeline(body.criterio, tracker=progress_actor)
    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)
    return JSONResponse(content=df.to_dict(orient="records"))
 
# Endpoint para estado de recálculo
@router.get("/recalculate/status", summary="Estado de cálculo en curso")
def get_recalculation_status():
    """
    Obtiene el estado actual del proceso de recálculo.
    
    Returns:
        JSON con el estado del cálculo
    """
    status = ray.get(progress_actor.get_status.remote())
    return JSONResponse(content=status)

# Endpoint para progreso de descarga
@router.get("/download/progress", summary="Progreso de la descarga de datos")
def get_download_progress():
    """
    Obtiene el progreso global de las descargas.
    
    Returns:
        JSON con porcentaje de progreso
    """
    return {"progress": download_progress}

# Endpoint para comparación de rendimientos
@router.get("/compare", summary="Comparamos el rendimiento secuencial contra el paralelo")
def compare_performance():
    """
    Compara el rendimiento de las versiones secuencial y paralela.
    
    Returns:
        JSON con tiempos de ejecución y uso de CPU
    """
    print("Ejecutando pipeline secuencial...")
    update_download_progress(25)  
    cpu_before_secuencial = measure_cpu_usage()
    start_time = time.time()
    result_secuencial = run_pipeline_sequential()
    secuencial_time = time.time() - start_time
    cpu_after_secuencial = measure_cpu_usage()
    print(f"ejecución secuencial: {secuencial_time:.2f} segundos")
    print(f"CPU en secuencial: {cpu_after_secuencial}%")
    
    update_download_progress(50) 

    print("\nEjecutando pipeline en paralelo...")
    cpu_before_paralelo = measure_cpu_usage()
    start_time = time.time()
    result_paralelo = run_parallel_pipeline()
    paralelo_time = time.time() - start_time
    cpu_after_paralelo = measure_cpu_usage()
    print(f"ejecución paralelo: {paralelo_time:.2f} segundos")
    print(f"CPU en paralelo: {cpu_after_paralelo}%")

    update_download_progress(100)  

    # Preparamos resultados de comparación
    comparison_result = {
        "secuencial": {
            "tiempo": secuencial_time,  # Tiempo ejecución secuencial
            "cpu": cpu_after_secuencial  # Uso de CPU secuencial
        },
        "paralelo": {
            "tiempo": paralelo_time,    # Tiempo ejecución paralelo
            "cpu": cpu_after_paralelo   # Uso de CPU paralelo
        }
    }

    return JSONResponse(content=comparison_result)