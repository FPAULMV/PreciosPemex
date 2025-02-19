from datetime import datetime, timedelta
import pyodbc
from decouple import config
import numpy as np
from Solicitud_sql import obtener_destinos_activos
import math



def enviar_logs(query):
    try:
        conn_str = (
            f"DRIVER={config('driver')};"
            f"SERVER={config('server')};"
            f"DATABASE={config('database')};"
            f"UID={config('user_name')};"
            f"PWD={config('password')}"
        )
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
    except pyodbc.Error as e:
        print("Error en la conexión o en la ejecución del query:", e)
    except Exception as e:
        print("Ocurrió un error inesperado:", e)
    else:
        conn.close()

# ENVIA EL DATA FRAME COMPLETO A SQL  
def enviar_df(df):
    df = df.replace({np.nan: None})
    try:
        conn_str = (
            f"DRIVER={config('driver')};"
            f"SERVER={config('server')};"
            f"DATABASE={config('database')};"
            f"UID={config('user_name')};"
            f"PWD={config('password')}"
        )
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            for index, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO Sinergia_Aux.dbo.Lista_Precios_Pemex (TAD, TADNombre, Magna, Premium, Diesel, Fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, row['TAD'], row['TADNombre'], row['MAGNA'], row['PREMIUM'], row['DIESEL'], row['Fecha'])
            conn.commit()
    except pyodbc.Error as e:
        print("Error en la conexión o en la ejecución del query:", e)
    except Exception as e:
        print("Ocurrió un error inesperado:", e)
    return True

def subir_precios(fecha):
    df = obtener_destinos_activos()
    nombre = f"Precios al {fecha}"
    nombre_archivo = f"Precios {fecha}.pdf"
    Tipo = 1
    FechaInicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    FechaFin = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')

    conn_str = (
        f"DRIVER={config('driver')};"
        f"SERVER={config('server')};"
        f"DATABASE={config('database')};"
        f"UID={config('user_name')};"
        f"PWD={config('password')}"
    )

    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                # Determina el tamaño de los lotes
                batch_size = 500
                total_rows = len(df)
                num_batches = math.ceil(total_rows / batch_size)

                for batch_num in range(num_batches):
                    # Selecciona un lote del DataFrame
                    start_idx = batch_num * batch_size
                    end_idx = min((batch_num + 1) * batch_size, total_rows)
                    batch_df = df.iloc[start_idx:end_idx]

                    queries = []
                    for _, row in batch_df.iterrows():
                        id_portal = row['ID Portal']
                        query_part = f"""
                        ('{nombre}', '{nombre_archivo}', '{id_portal}', {Tipo}, '{FechaInicio}', '{FechaFin}', '{FechaInicio}')
                        """
                        queries.append(query_part)

                    # Unir todas las partes del query en una sola instrucción SQL
                    full_query = f"""
                    INSERT INTO NexusFuel.CardSystem.ArchivosGenerales 
                    (Nombre, nombreArchivo, Destino, Tipo, FechaInicio, FechaFin, FechaCreacion) 
                    VALUES {','.join(queries)};
                    """
                    print(f"Ejecutando lote {batch_num + 1} de {num_batches}")
                    print(f"------------------------------\n{full_query}\n------------------------------")
                    
                    # Ejecutar el query completo para el lote actual
                    cursor.execute(full_query)
                    conn.commit()
    except pyodbc.Error as e:
        print("Error en la conexión o en la ejecución del query:", e)
    except Exception as e:
        print("Ocurrió un error inesperado:", e)

