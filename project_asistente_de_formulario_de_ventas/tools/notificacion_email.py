import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# --- CAMBIO CLAVE AQUÍ ---
# Le decimos a dotenv que busque el archivo .env un nivel ARRIBA,
# en la carpeta principal del proyecto, para que encuentre las credenciales.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Obtener credenciales desde las variables de entorno
APP_PASSWORD_GMAIL = os.getenv("APP_PASSWORD_GMAIL") #ESTO SE CAMBIA EN EL .env *************************************************************************
CORREO_REMITENTE = os.getenv("EMAIL_REMITENTE") #ESTO SE CAMBIA EN EL .env ******************************************************************************

def enviar_correo_bienvenida(nombre_destinatario: str, email_destinatario: str, contenido_html: str) -> str:
    """
    Envía un correo electrónico de bienvenida a un usuario que se ha registrado.

    Args:
        nombre_destinatario: El nombre de la persona a la que se le envía el correo.
        email_destinatario: La dirección de correo del destinatario.
        contenido_html: El cuerpo del correo en formato HTML.

    Returns:
        Un mensaje de confirmación o de error.
    """
    if not all([APP_PASSWORD_GMAIL, CORREO_REMITENTE]):
        error_msg = ("Error: Faltan las variables de entorno 'APP_PASSWORD_GMAIL' o 'EMAIL_REMITENTE' en tu archivo .env. "
                     f"Asegúrate de que el archivo .env está en '{os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}'")
        print(f"❌ {error_msg}")
        return error_msg

    try:
        # Crear el objeto del correo
        msg = EmailMessage()
        msg["From"] = CORREO_REMITENTE
        msg["To"] = email_destinatario
        msg["Subject"] = f"PRUEBA DE CORREO: ¡Gracias por tu interés, {nombre_destinatario}!"
        
        # Establecer el contenido como HTML
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(contenido_html, charset='utf-8')

        # Conectar al servidor SMTP de Gmail y enviar
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(CORREO_REMITENTE, APP_PASSWORD_GMAIL)
            smtp.send_message(msg)
        
        print(f"✅ Correo enviado exitosamente a: {email_destinatario}")
        return f"Correo de bienvenida enviado exitosamente a {email_destinatario}."

    except Exception as e:
        error_msg = f"Error inesperado al enviar el correo: {e}"
        print(f"❌ {error_msg}")
        return error_msg



# --- Bloque de Prueba para Ejecución Directa ---
# if __name__ == '__main__':
#     print("--- Iniciando prueba de envío de correo electrónico ---")

#     # --- ¡IMPORTANTE! ---
#     # Cambia esta dirección de correo por una a la que TENGAS ACCESO para poder verificar que el correo llega.
#     email_de_prueba_destinatario = "kevin.inofuente.colque.br@gmail.com"
    
#     # Datos de prueba que quieres enviar
#     nombre_prueba = "Usuario de Prueba"
#     contenido_html_prueba = """
#     <html>
#       <body>
#         <h1>¡Hola!</h1>
#         <p>Este es un correo de prueba generado directamente desde el script <code>notificacion_email.py</code>.</p>
#         <p>Si estás leyendo esto, ¡la función de envío de correo funciona perfectamente!</p>
#       </body>
#     </html>
#     """

#     # Verificamos que las credenciales se hayan cargado antes de llamar a la función
#     if not all([APP_PASSWORD_GMAIL, CORREO_REMITENTE]):
#          print("❌ No se pueden ejecutar las pruebas porque faltan las credenciales en el archivo .env.")
#     else:
#         print(f"Intentando enviar correo desde '{CORREO_REMITENTE}' hacia '{email_de_prueba_destinatario}'...")
#         # Llamamos a la función directamente
#         resultado = enviar_correo_bienvenida(
#             nombre_destinatario=nombre_prueba,
#             email_destinatario=email_de_prueba_destinatario,
#             contenido_html=contenido_html_prueba
#         )

#         print("\n--- Resultado de la prueba ---")
#         print(resultado)
#         print("---------------------------------")
#         print(f"Por favor, verifica la bandeja de entrada de '{email_de_prueba_destinatario}' para confirmar la recepción del correo.")