# Importación de bibliotecas necesarias
import pandas as pd  # Para manejo y análisis de datos
import matplotlib.pyplot as plt  # Para generación de gráficos

def generate_plot():
    """
    Genera un gráfico comparativo de retornos acumulados entre la estrategia basada en Twitter
    y el índice Nasdaq (QQQ), y guarda el resultado como imagen PNG.
    
    Returns:
        str: Ruta del archivo de imagen generado ("output/returns_plot.png")
    """
    
    # 1. Carga y preparación de datos
    # Leemos el archivo CSV con los retornos acumulados
    df = pd.read_csv("output/cumulative_returns.csv", parse_dates=["Date"])
    # Convertimos la columna Date en el índice del DataFrame
    df.set_index("Date", inplace=True)

    # 2. Configuración del gráfico
    # Creamos una figura con tamaño 10x5 pulgadas
    plt.figure(figsize=(10, 5))
    
    # 3. Graficamos las series de datos
    # Línea principal para la estrategia Twitter (continua, gruesa)
    plt.plot(df["portfolio_returns"], 
             label="Estrategia Twitter", 
             linewidth=2)
    
    # Línea comparativa para el Nasdaq (discontinua)
    plt.plot(df["nasdaq_return"], 
             label="Nasdaq (QQQ)", 
             linestyle="--")

    # 4. Personalización del gráfico
    # Añadimos título y etiquetas de ejes
    plt.title("Retornos acumulados")
    plt.xlabel("Fecha")
    plt.ylabel("Retorno acumulado")
    
    # Mostramos leyenda y cuadrícula
    plt.legend()
    plt.grid(True)
    
    # Ajustamos el layout para evitar solapamientos
    plt.tight_layout()

    # 5. Guardado y cierre
    # Definimos la ruta de guardado
    plot_path = "output/returns_plot.png"
    # Guardamos el gráfico como PNG
    plt.savefig(plot_path)
    # Cerramos la figura para liberar memoria
    plt.close()
    
    # Retornamos la ruta donde quedó guardado el gráfico
    return plot_path