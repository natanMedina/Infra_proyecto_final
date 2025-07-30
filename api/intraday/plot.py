# Configuración inicial para matplotlib - importante para entornos sin interfaz gráfica
import matplotlib
matplotlib.use("Agg")  # Establece el backend 'Agg' para evitar problemas en servidores

# Importación de bibliotecas necesarias
import matplotlib.pyplot as plt  # Para generación de gráficos
import os  # Para manejo de rutas y directorios

def generate_plot(df, output_path="output/estrategia_plot.png"):
    """
    Genera y guarda un gráfico del retorno acumulado de la estrategia intradía.
    
    Args:
        df (DataFrame): DataFrame de pandas con los datos a graficar.
                        Debe contener columnas 'datetime' y 'cumulative_strategy_return'.
        output_path (str): Ruta donde se guardará la imagen generada.
                          Por defecto es "output/estrategia_plot.png".
    
    Returns:
        str: Ruta donde se guardó el archivo de imagen.
    """
    
    # Crea el directorio de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Configura el tamaño de la figura (ancho, alto en pulgadas)
    plt.figure(figsize=(10, 5))
    
    # Crea el gráfico de línea principal
    plt.plot(
        df["datetime"],  # Eje X - fechas
        df["cumulative_strategy_return"],  # Eje Y - retorno acumulado
        label="Estrategia Intradía",  # Etiqueta para la leyenda
        linewidth=2,  # Grosor de la línea
        color="blue"  # Color de la línea
    )
    
    # Configuración del título y etiquetas de ejes
    plt.title("Retorno Acumulado - Estrategia Intradía")  # Título del gráfico
    plt.xlabel("Fecha")  # Etiqueta eje X
    plt.ylabel("Retorno acumulado")  # Etiqueta eje Y
    
    # Configuraciones adicionales del gráfico
    plt.grid(True)  # Habilita la cuadrícula
    plt.xticks(rotation=45)  # Rota las etiquetas del eje X 45 grados
    plt.tight_layout()  # Ajusta el layout para evitar cortes
    
    # Muestra la leyenda
    plt.legend()
    
    # Guarda el gráfico como imagen PNG
    plt.savefig(output_path)
    
    # Cierra la figura para liberar memoria
    plt.close()
    
    # Retorna la ruta donde se guardó el archivo
    return output_path