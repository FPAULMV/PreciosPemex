import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from decouple import config
import Principal as P
import sys

class SendMail:
    def success_mail(file_names):

        # "maria.jauregui@secmexico.com"
        destinos = ["paul.morales@secmexico.com",
                    "maria.jauregui@secmexico.com"
                    ]

        # Configuración del servidor y credenciales
        SMTP_SERVER = "smtp.office365.com"
        SMTP_PORT = 587
        EMAIL = "servicios.soporte@secmexico.com"
        PASSWORD = "Hux58495"
        # Configuración del correo
        destinatarios = destinos
        asunto = f"{config('ASUNTO')}"
        cuerpo_html = f"{config('SUCCESS_HTML')}"

        with open(cuerpo_html,"r", encoding="utf-8") as file:
            cuerpo_html = file.read()


        # Crear mensaje
        mensaje = MIMEMultipart()
        mensaje["From"] = EMAIL
        mensaje["To"] = ", ".join(destinatarios)
        mensaje["Subject"] = asunto

        # Adjuntar cuerpo en formato HTML
        mensaje.attach(MIMEText(cuerpo_html, "html"))

        file_path = f"{config('ruta_temp')}"
        # Adjuntar archivo
        for name in file_names:
            ruta_archivo = f"{file_path}\\{name}"
            with open(ruta_archivo, "rb") as adjunto:
                parte = MIMEBase("application", "octet-stream")
                parte.set_payload(adjunto.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    "Content-Disposition",
                    f"attachment; filename={name}"
                )
                mensaje.attach(parte)

        # Enviar correo
        try:
            servidor = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            servidor.starttls()
            servidor.login(EMAIL, PASSWORD)
            servidor.sendmail(EMAIL, destinatarios, mensaje.as_string())
            print("Correo enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
        finally:
            servidor.quit()


    def error_mail():
        pass




if __name__ == '__main__':
    i = SendMail.success_mail()

