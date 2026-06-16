# agent.py

from google.adk.agents import Agent
from tools.registro_sheet import registrar_interes_en_sheet
from tools.notificacion_email import enviar_correo_bienvenida

# Información sobre los cursos que el agente usará para generar los correos.
# Esta información podría venir de una base de datos o una búsqueda en el futuro.
INFORMACION_CURSOS = {
    "fastapi": {
        "nombre_completo": "Desarrollo de API's con FastAPI",
        "descripcion": """
        FastAPI es un framework web moderno y de alto rendimiento para construir APIs con Python. 
        Se destaca por su increíble velocidad, la generación automática de documentación interactiva 
        (gracias a OpenAPI y Swagger UI) y un sistema de tipos basado en type hints de Python que minimiza 
        errores y mejora la experiencia de desarrollo. En este curso, aprenderás a crear APIs RESTful 
        robustas, seguras y listas para producción.
        """
    },
    "django": {
        "nombre_completo": "Curso de Django",
        "descripcion": """
        Django es un framework web de alto nivel que fomenta el desarrollo rápido y un diseño limpio y 
        pragmático. Conocido por su filosofía de "baterías incluidas", Django ofrece un ORM potente, 
        un panel de administración automático, un sistema de autenticación seguro y mucho más, todo listo 
        para usar. Es ideal para construir aplicaciones complejas y escalables, desde blogs hasta 
        plataformas de e-commerce.
        """
    }
}


root_agent = Agent(
    name="RegistrationAgent",
    model="gemini-2.5-flash",
    description="Agente para registrar el interés de usuarios en cursos de programación.",
    tools=[
        registrar_interes_en_sheet,
        enviar_correo_bienvenida,
    ],
    instruction=f"""
      # Misión del Agente: Procesador de Registros de Cursos

      Tu único objetivo es procesar el registro de un nuevo usuario utilizando tus herramientas. La petición del usuario contendrá toda la información que necesitas.

      Tu proceso debe ser:
      1.  Usa la herramienta `registrar_interes_en_sheet` para guardar la información del usuario en la hoja de cálculo. Debes llamar a esta herramienta por cada curso de interés.
      2.  Usa la herramienta `enviar_correo_bienvenida` para enviar una confirmación por email al usuario. El contenido del correo debe incluir una descripción del curso o cursos seleccionados.
      3.  Al finalizar, responde con un breve resumen confirmando las acciones realizadas.

      Aquí tienes la información de los cursos que podrías necesitar para el correo:
      - FastAPI: {INFORMACION_CURSOS['fastapi']['descripcion']}
      - Django: {INFORMACION_CURSOS['django']['descripcion']}
   """,
)