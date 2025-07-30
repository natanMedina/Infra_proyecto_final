# Importación de bibliotecas necesarias
import pandas as pd  # Para manejo y análisis de datos

def get_cumulative_returns():
    """
    Lee y retorna un DataFrame con los retornos acumulados de la estrategia y benchmark.
    
    Carga los datos desde un archivo CSV y convierte la columna de fechas al tipo datetime.
    
    Returns:
        pd.DataFrame: DataFrame con las columnas:
            - Date (datetime): Fechas de los retornos
            - portfolio_returns: Retornos acumulados de la estrategia
            - nasdaq_return: Retornos acumulados del benchmark (NASDAQ QQQ)
    """
    
    # Lee el archivo CSV ubicado en 'output/cumulative_returns.csv'
    # Parsea automáticamente la columna 'Date' como datetime
    df = pd.read_csv('output/cumulative_returns.csv', parse_dates=['Date'])
    
    # Retorna el DataFrame con los datos cargados
    return df