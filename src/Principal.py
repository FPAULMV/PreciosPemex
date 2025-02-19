from decouple import config
import PyPDF2
import os
import Extraer_Informacion as EI
import Solicitud_sql as SS
import Logs as LO
import sendmail
import sys
import shutil
from datetime import datetime

class Inicial:
    """"""
    def __init__(self):
        self.dir_path = f"{config('ruta_temp')}"
        self.name_item = f"{config('nombre_temp')}"
        list_items = self.find_archivos() # ACTUALIZACION: Debe de notificar si no encontro el archivo por correo.
        fechas = self.lectura_fecha(list_items)
        list_fechas = SS.obtener_fechas_sql()
        print(f"Fechas obtenidas!")

        self.names = []
        for f in fechas:
            if f in list_fechas:
                msg = f"La fecha: {f} ya esta registrada"
                print(msg)
                # sys.exit()
            else:
                print(f"Trabajando con la fecha {f}")
                file_name = self.copiar_y_renombrar(f, self.ruta)
                df = EI.extrae_pdf_tablas(f, self.ruta)
                LO.enviar_df(df)
                # LO.subir_precios(f)
                self.names.append(file_name)
                print(f"Los nombres de los archivos son:\n{self.names}")
                print(f"Enviando correo.")
                sendmail.SendMail.success_mail(self.names)
        self.borrar_temp(self.ruta)
        print(f"Archivo: {self.ruta} eliminado.")
        print("Fin.")
    
    def find_archivos(self):
        self.archivos = []
        for a in os.listdir(self.dir_path):
            if self.name_item in a.lower() and ".pdf" in a.lower():
                self.archivos.append(a)
                # print(f"El archivo es: {a}")

        if self.archivos:
            msg = f"Los archivos encontrados son:\n{self.archivos}"
            print(msg)
        else:
            time_now = datetime.now().strftime("%H:%M:%S")
            time_max = "20:30:00"
            if time_now > time_max:
                msg = f"No se encontro el archivo.\n"
                print(msg)
                exit()
            else:
                exit()
        return self.archivos
    
    def lectura_fecha(self, list_items):
        self.i = list_items[0]
        self.ruta = f"{config('ruta_temp')}\\{self.i}"
        with open(self.ruta, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
        
        lines = text.split('\n')
        fechas = []
        for line in lines:
            fechas.extend(EI.extraer_fechas(line))
        return fechas

    def borrar_temp(self, ruta):
        try:
            existe = os.path.exists(ruta)
            if existe == True:
                os.remove(ruta) 
            else:
                print("El documento no existe")      
        except:
            print("El documento no existe")
            pass
    
    def copiar_y_renombrar(self, nuevo_nombre, archivo_temporal):
        carpeta_destino = f"{config('ruta_temp')}"
        self.nombre = f"Precios {nuevo_nombre}.pdf"

        # Asegurarse de que la carpeta de destino existe
        if os.path.exists(archivo_temporal):
            print("El documento existe")
            # Definir la ruta completa del archivo de destino
            archivo_destino = os.path.join(carpeta_destino, self.nombre)
            # Copiar el archivo
            shutil.copy2(archivo_temporal, archivo_destino)
            print(f"Archivo copiado en: {carpeta_destino}\nCon el nombre: {self.nombre}")
            return self.nombre
        else:
            print("No se encontro el documento")
            pass


if __name__ == '__main__':
    i = Inicial()
    
