"""
API REST del agente Text-to-SQL de CitiBike (FastAPI + Google ADK).

Expone el agente `root_agent` definido en agent.py como un servicio HTTP para
consumirlo desde cualquier cliente (frontend, Postman, curl, otro servicio).

Endpoints:
    GET  /health                      Estado del servicio.
    POST /chat                        Envía una pregunta en lenguaje natural y
                                      devuelve la respuesta del agente y el SQL
                                      que ejecutó. Mantiene la conversación si se
                                      reenvía el mismo `session_id`.
    GET  /sessions/{user_id}/{id}     Historial de una sesión.
    DELETE /sessions/{user_id}/{id}   Borra una sesión.

Arranque (desde la raíz del repo, con las credenciales ADC ya creadas):
    uvicorn project_agent_text_to_sql_bigquery.main:app --reload --port 8080
o bien, desde esta carpeta:
    python main.py

Documentación interactiva: http://localhost:8080/docs
"""

import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel, Field

try:
    from .agent import root_agent
except ImportError:  # Ejecutado como script (python main.py) o `uvicorn main:app` desde esta carpeta
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from project_agent_text_to_sql_bigquery.agent import root_agent

# Carga el .env que está junto a este archivo (GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GOOGLE_GENAI_USE_VERTEXAI)
load_dotenv(Path(__file__).resolve().parent / ".env")

# --- Variables de entorno ---
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8080"))
# Orígenes del frontend autorizados (separados por coma). Por defecto, el dev server de Vite.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

# URL de la base de datos de sesiones (historial). Ej. Cloud SQL vía Auth Proxy:
#   postgresql+asyncpg://adk:<CONTRASEÑA>@127.0.0.1:5432/adk_sessions
# Si no se define, se usa SQLite local junto a este archivo.
SESSION_DB_URL = os.getenv(
    "SESSION_DB_URL",
    f"sqlite+aiosqlite:///{Path(__file__).resolve().parent / '.adk' / 'api_sessions.db'}",
)

# --- Constantes ---
APP_NAME = "text_to_sql_citibike"
DEFAULT_USER_ID = "user"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(APP_NAME)


# ---------------------------------------------------------------------------
# Esquemas de entrada / salida
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta en lenguaje natural para el agente.")
    user_id: str = Field(DEFAULT_USER_ID, description="Identificador del usuario que consulta.")
    session_id: str | None = Field(
        None,
        description="Sesión a continuar. Si se omite, se crea una nueva y se devuelve en la respuesta.",
    )


class ChatResponse(BaseModel):
    session_id: str
    user_id: str

    response: str = Field(
        ...,
        description="Respuesta final del agente en lenguaje natural."
    )

    sql_queries: list[str] = Field(
        default_factory=list,
        description="Consultas SQL que el agente ejecutó en BigQuery."
    )

    charts: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Visualizaciones generadas por el agente."
    )


class SessionMessage(BaseModel):
    role: str
    text: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    messages: list[SessionMessage]


# ---------------------------------------------------------------------------
# Runner del ADK: se crea una sola vez al arrancar el servidor.
# Las sesiones se persisten en SESSION_DB_URL (Cloud SQL / PostgreSQL o SQLite);
# el ADK crea las tablas (sessions, events, app_states, user_states) al arrancar.
# ---------------------------------------------------------------------------
(Path(__file__).resolve().parent / ".adk").mkdir(exist_ok=True)
session_service = DatabaseSessionService(db_url=SESSION_DB_URL)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Agente '%s' listo. Modelo: %s", root_agent.name, root_agent.model)
    logger.info("Sesiones persistidas en: %s", SESSION_DB_URL.split("@")[-1] if "@" in SESSION_DB_URL else SESSION_DB_URL)
    yield
    await runner.close()


app = FastAPI(
    title="Agente Text-to-SQL de CitiBike",
    description="Convierte preguntas en lenguaje natural en consultas SQL sobre BigQuery y devuelve la respuesta.",
    version="1.0.0",
    lifespan=lifespan,
)

# Permite que el frontend React (project_agente_text_to_sql_bigquery_frontend) llame a la API desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def get_or_create_session(user_id: str, session_id: str | None):
    """Devuelve la sesión indicada o crea una nueva si no existe / no se indicó."""
    if session_id:
        session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        if session:
            return session
    return await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id or str(uuid.uuid4())
    )


async def run_agent(user_id: str, session_id: str, message: str) -> tuple[str, list[str], list[dict[str, Any]]]:
    """Ejecuta el agente y devuelve respuesta, consultas SQL y gráficos generados."""
    
    content = types.Content(role="user", parts=[types.Part(text=message)])
    final_text: list[str] = []
    sql_queries: list[str] = []
    charts: list[dict[str, Any]] = []

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # Capturar consultas SQL ejecutadas
        for call in event.get_function_calls():
            if (
                call.name == "run_sql_query"
                and call.args
                and "query" in call.args
            ):
                sql_queries.append(call.args["query"])

        # Capturar gráficos generados por create_visualization
        for function_response in event.get_function_responses():
            if function_response.name == "create_visualization":

                payload = function_response.response

                # Algunas versiones de ADK pueden envolver
                # la respuesta dentro de "result"
                if (
                    isinstance(payload, dict)
                    and "result" in payload
                    and isinstance(payload["result"], dict)
                ):
                    payload = payload["result"]

                if (
                    isinstance(payload, dict)
                    and payload.get("status") == "success"
                    and payload.get("chart")
                ):
                    charts.append(payload["chart"])

        # Capturar respuesta textual final
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
        ):
            final_text.extend(
                part.text
                for part in event.content.parts
                if part.text
            )

    return "".join(final_text).strip(), sql_queries, charts


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["sistema"])
async def health():
    return {"status": "ok", "agent": root_agent.name, "model": root_agent.model}


@app.post("/chat", response_model=ChatResponse, tags=["agente"])
async def chat(request: ChatRequest):
    session = await get_or_create_session(request.user_id, request.session_id)
    try:
        response, sql_queries, charts = await run_agent(request.user_id, session.id, request.message)
    except Exception as exc:  # errores de Vertex AI / BigQuery / credenciales
        logger.exception("Error ejecutando el agente")
        raise HTTPException(status_code=502, detail=f"Error al ejecutar el agente: {exc}") from exc

    if not response:
        response = "El agente no produjo una respuesta final."

    return ChatResponse(
        session_id=session.id, user_id=request.user_id, response=response, sql_queries=sql_queries, charts=charts
    )


@app.get("/sessions/{user_id}/{session_id}", response_model=SessionResponse, tags=["sesiones"])
async def get_session(user_id: str, session_id: str):
    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    messages = [
        SessionMessage(role=event.content.role or "model", text="".join(p.text for p in event.content.parts if p.text))
        for event in session.events
        if event.content and event.content.parts and any(p.text for p in event.content.parts)
    ]
    return SessionResponse(session_id=session.id, user_id=user_id, messages=messages)


@app.delete("/sessions/{user_id}/{session_id}", status_code=204, tags=["sesiones"])
async def delete_session(user_id: str, session_id: str):
    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    await session_service.delete_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
