import PyPDF2
import pandas as pd
import re
from decouple import config
from datetime import datetime, timedelta


def extrae_pdf_tablas(fecha, ruta):
    with open(ruta, 'rb') as file:
        pdf_read = PyPDF2.PdfReader(file)
        
        num_paginas = len(pdf_read.pages) - 1
        datos = []

        for pagina_num in range(num_paginas):
            pagina = pdf_read.pages[pagina_num]
            texto = pagina.extract_text()

            lineas = texto.split('\n')
            lineas = [linea.strip() for linea in lineas if linea.strip()]

            # Diccionario de frases a descartar con expresiones regulares
            frases_descartadas = {
                1: "CONTENIDO MÍNIMO 87",
                2: "OCTANOSGASOLINA CON",
                3: "OCTANOSDIESEL",
                4: "Precios de venta en TAR aplicables",
                5: r'para el (\d{1,2}) de (\w+) del (\d{4})',
                6: r'del (\d{1,2}) al (\d{1,2}) de (\w+) de (\d{4})',
                7: r'del (\d{1,2}) de (\w+) al (\d{1,2}) de (\w+) de (\d{4})',
                8: "Nota.- Pr",
                9: "NOM-",
                10: "TAR",
                11: "Artículo Decimo Primero",
                12: "Esta información es confiden",
                13: "31 de diciembre de 2018.",
                14: "total o parcial, conforme",
                15: "PEMEX TRANSFORMACIÓN INDUSTRIAL",
                16: "SUBDIRECCIÓN DE COMERCIALIZACIÓN",
                17: "REGIÓN",
                18: "GASOLINA",
                19: "MAGNA",
                20: "CONTENIDO MÍNIMO 91",
                21: "PREMIUM",
                22: "DIESEL"
            }

            # Filtrar las líneas que no contienen las frases descartadas
            lineas_filtradas = [linea for linea in lineas if not any(re.search(frase, linea) for frase in frases_descartadas.values())]
            regex_lagos_de_moreno = r'^(\d+)\s+LAGOS DE MORENO\s+(\d+,\d+\.\d+)\s+(\d+,\d+\.\d+)$'
            for linea in lineas_filtradas:
                if "LAGOS DE MORENO" in linea:
                    match_lagos_de_moreno = re.match(regex_lagos_de_moreno, linea)
                    if match_lagos_de_moreno:
                        tad, magna, diesel = match_lagos_de_moreno.groups()
                        datos.append((tad, "LAGOS DE MORENO", magna, None, diesel))
                else:
                    # Usar la expresión regular original para las demás líneas
                    match = re.match(r'^(\d+)\s+([\w\s\*]+)\s+(\d+,\d+\.\d+)\s+(\d+,\d+\.\d+)\s+(\d+,\d+\.\d+)$', linea)
                    if match:
                        datos.append(match.groups())


    # Definir nombres de columnas
    columnas = ["TAD", "TADNombre", "MAGNA", "PREMIUM", "DIESEL"]

    # Crear DataFrame de pandas
    df = pd.DataFrame(datos, columns=columnas)
    df["TAD"] = df["TAD"].astype(int)
    df["MAGNA"] = df["MAGNA"].str.replace(",", "").astype(float)/1000
    df["PREMIUM"] = df["PREMIUM"].str.replace(",", "").astype(float)/1000
    df["DIESEL"] = df["DIESEL"].str.replace(",", "").astype(float)/1000
    df["Fecha"] = fecha

    return df


# ----------------------------------------------------------------
# BUSCA LOS PATRONES DE EXPRECIONES REGULARES EN LINEAS DE TEXTO Y DEVUELVE UNA FECHA O UN RANGO DE FECHAS.
"""
Depende de la funcion "lecura_fechas".
"""
def extraer_fechas(texto):
    simple_fecha_patron = r'para el (\d{1,2}) de (\w+) del (\d{4})'
    mismo_mes_patron = r'del (\d{1,2}) al (\d{1,2}) de (\w+) de (\d{4})'
    diferente_mes_patron = r'del (\d{1,2}) de (\w+) al (\d{1,2}) de (\w+) de (\d{4})'
    
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    fechas = []

    # Fecha simple
    simple_fecha_coincidencia = re.search(simple_fecha_patron, texto)
    if simple_fecha_coincidencia:
        dia = int(simple_fecha_coincidencia.group(1))
        mes_nombre = simple_fecha_coincidencia.group(2).lower()
        anio = int(simple_fecha_coincidencia.group(3))
        mes = meses[mes_nombre]
        fecha = datetime(anio, mes, dia)
        fechas.append(fecha.strftime('%Y-%m-%d'))

    # Rango de fechas dentro del mismo mes
    mismo_mes_coincidencia = re.search(mismo_mes_patron, texto)
    if mismo_mes_coincidencia:
        dia_inicio = int(mismo_mes_coincidencia.group(1))
        dia_fin = int(mismo_mes_coincidencia.group(2))
        mes_nombre = mismo_mes_coincidencia.group(3).lower()
        anio = int(mismo_mes_coincidencia.group(4))
        mes = meses[mes_nombre]
        for dia in range(dia_inicio, dia_fin + 1):
            fecha = datetime(anio, mes, dia)
            fechas.append(fecha.strftime('%Y-%m-%d'))

    # Rango de fechas entre dos meses diferentes
    diferente_mes_coincidencia = re.search(diferente_mes_patron, texto)
    if diferente_mes_coincidencia:
        dia_inicio = int(diferente_mes_coincidencia.group(1))
        mes_inicio_nombre = diferente_mes_coincidencia.group(2).lower()
        dia_fin = int(diferente_mes_coincidencia.group(3))
        mes_fin_nombre = diferente_mes_coincidencia.group(4).lower()
        anio = int(diferente_mes_coincidencia.group(5))
        mes_inicio = meses[mes_inicio_nombre]
        mes_fin = meses[mes_fin_nombre]
        
        fecha_inicio = datetime(anio, mes_inicio, dia_inicio)
        fecha_fin = datetime(anio, mes_fin, dia_fin)
        
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            fechas.append(fecha_actual.strftime('%Y-%m-%d'))
            fecha_actual += timedelta(days=1)
    return fechas

