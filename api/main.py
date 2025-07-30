# Importación de bibliotecas necesarias
import ray  # Framework para computación distribuida
from ray import serve  # Para servir modelos y aplicaciones
from fastapi import FastAPI  # Framework para construir APIs
from fastapi.middleware.cors import CORSMiddleware  # Para manejar CORS
from api.sentiment.endpoints import router as sentiment_router  # Endpoints de análisis de sentimiento
from api.intraday.endpoints import router as intradaily_router  # Endpoints de datos intradía
import time  # Para manejar tiempos de espera

# Configuración inicial de la aplicación FastAPI
app = FastAPI(
    title="API de Análisis de Portafolio",  # Título de la API
    description="API para análisis de estrategias de inversión basadas en sentimiento e intradía"  # Descripción
)

# Configuración de CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite solicitudes desde este origen (típicamente frontend)
    allow_credentials=True,  # Permite cookies y credenciales
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Registro de routers (conjuntos de endpoints)
app.include_router(sentiment_router)  # Endpoints de análisis de sentimiento
app.include_router(intradaily_router)  # Endpoints de datos intradía

# Configuración del deployment con Ray Serve
@serve.deployment  # Decorador para crear un deployment de Ray Serve
@serve.ingress(app)  # Indica que este deployment servirá la app FastAPI
class UnifiedAPI:
    """Clase contenedora para la API unificada"""
    pass

# Punto de entrada principal (solo se ejecuta al correr el script directamente)
if __name__ == "__main__":
    # Inicialización de Ray
    ray.init(
        ignore_reinit_error=True,  # Evita errores si Ray ya estaba inicializado
        include_dashboard=True  # Habilita el dashboard de Ray (opcional)
    )
    
    # Inicia el servidor de Ray Serve
    serve.start(
        http_options={"host": "0.0.0.0", "port": 8000}  # Configuración del servidor HTTP
    )
    
    # Monta la API unificada en el servidor
    serve.run(UnifiedAPI.bind())

    # Mensaje de confirmación
    print("Ray Serve está corriendo en http://localhost:8000")
    print("Dashboard de Ray disponible en http://localhost:8265")  # Si el dashboard está habilitado
    
    # 💤 Bucle infinito para mantener el servicio activo
    try:
        while True:
            time.sleep(3600)  # Espera 1 hora entre iteraciones
    except KeyboardInterrupt:
        # Manejo de interrupción por teclado (Ctrl+C)
        print("\nApagando Ray Serve...")
        serve.shutdown()  # Apaga Ray Serve correctamente
        ray.shutdown()  # Cierra Ray