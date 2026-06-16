# main.py

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Importa el agente y las clases necesarias del ADK
from agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# --- Configuración ---
APP_NAME = "course_app"
USER_ID = "frontend_user"
SESSION_ID = "session01"

# Inicializar servicios del ADK
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

# --- Lógica de Arranque y Apagado (Solución al RuntimeError) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto se ejecuta ANTES de que la aplicación empiece a aceptar peticiones
    print("Iniciando la aplicación y creando sesión...")
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print("Sesión creada. La aplicación está lista.")
    yield
    # Esto se ejecutaría al apagar el servidor (opcional)
    print("Apagando la aplicación.")

# --- Creación de la Aplicación FastAPI ---
app = FastAPI(lifespan=lifespan) # <-- Registramos el lifespan aquí

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Funciones Auxiliares y Endpoints ---
# main.py

def build_prompt(data: dict) -> str:
    """
    Construye un prompt claro y directo para el agente, reforzando
    la necesidad de usar sus herramientas.
    """
    # Extraemos los datos del JSON para que el prompt sea más legible si queremos
    dp = data.get("datos_personales", {})
    nombre = dp.get("nombre", "N/A")
    apellido = dp.get("apellido", "N/A")
    email = dp.get("email", "N/A")
    cursos = ", ".join(data.get("cursos_interes", ["ninguno"]))
    
    # El prompt ahora es una orden directa
    return (
        f"¡Atención, agente! Un nuevo usuario se ha registrado a través del formulario. "
        f"Tu misión es usar tus herramientas para procesar este registro. "
        f"1. Llama a la herramienta 'registrar_interes_en_sheet' para guardar los datos. "
        f"2. Llama a la herramienta 'enviar_correo_bienvenida' para notificar al usuario. "
        f"Aquí están los datos del formulario:\n"
        f"Nombre: {nombre}\n"
        f"Apellido: {apellido}\n"
        f"Email: {email}\n"
        f"Cursos de interés: {cursos}\n"
        f"JSON completo original por si lo necesitas: {data}"
    )



async def call_agent(prompt: str) -> str:
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    final_response_text = "El agente procesó la solicitud pero no proporcionó una respuesta de texto final."
    
    try:
        # El runner se encarga de todo el ciclo: llamar al modelo, ejecutar la herramienta y obtener la respuesta final.
        async for evt in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            # Nos interesa únicamente la respuesta final de texto que el agente genera DESPUÉS de usar las herramientas.
            if hasattr(evt, 'is_final_response') and evt.is_final_response() and evt.content:
                 final_response_text = evt.content.parts[0].text or final_response_text
                 # Una vez que tenemos la respuesta final, podemos salir.
                 break
        
        # Después de que el bucle termina, devolvemos la respuesta que encontramos.
        return final_response_text

    except Exception as e:
        print(f"Error CRÍTICO durante la ejecución del runner: {e}")
        # En caso de un error real, lo devolvemos para que el frontend lo sepa.
        return f"Error interno del agente: {e}"

@app.post("/invocations")
async def invocations_proxy(request: Request):
    data = await request.json()
    prompt = build_prompt(data)
    
    print("--- PROMPT ENVIADO AL AGENTE ---")
    print(prompt)
    print("--------------------------------")
    
    agent_response = await call_agent(prompt)
    
    print("--- RESPUESTA RECIBIDA DEL AGENTE ---")
    print(agent_response)
    print("-------------------------------------")
    
    return {"resultado": agent_response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

#python3 main.py