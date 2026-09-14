# agent.py

"""
Agente Text-to-SQL de CitiBike (Google ADK).

El system prompt NO vive aquí: se carga desde prompt/system_prompt.yaml
(clave `system_prompt`), que además lleva la metadata del prompt (nombre, versión, etc.).
"""

from pathlib import Path

import yaml

# De la librería del ADK, importamos la clase "Agent", que es el chasis o el esqueleto sobre el cual montaremos todo lo demás.
from google.adk.agents import Agent

# El "." al principio significa que es una importación "relativa" desde la misma carpeta del proyecto.
from .tools.run_sql_query import run_sql_query
from .tools.create_visualization import create_visualization

# --- Constantes ---
PROMPT_PATH = Path(__file__).resolve().parent / "prompt" / "system_prompt.yaml"


def load_system_prompt(path: Path = PROMPT_PATH, **variables: str) -> str:
    """Lee el YAML del prompt y reemplaza los placeholders declarados en `variables:` (formato {nombre})."""
    prompt_cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    system_prompt: str = prompt_cfg["system_prompt"]
    for name in prompt_cfg.get("variables") or []:
        if name not in variables:
            raise KeyError(f"El prompt declara la variable '{name}' pero no se pasó un valor para ella")
        system_prompt = system_prompt.replace(f"{{{name}}}", variables[name])
    return system_prompt


# --- LA DEFINICIÓN DEL AGENTE - Ensamblando las Piezas ---
# Creamos una instancia del agente configurando su cerebro (modelo), sus herramientas y su personalidad (prompt).
# Lo asignamos a la variable `root_agent` porque es el nombre que el ADK busca por defecto al iniciarse.
root_agent = Agent(
    name="SqlAgent",
    model="gemini-2.5-flash",  # Simplemente el nombre del modelo.
    description="Agente Analista de Datos de CitiBike",
    tools=[
        run_sql_query,
        create_visualization,
    ],
    instruction=load_system_prompt(),
)
