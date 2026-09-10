# ADK-Agents

Proyecto de agentes ADK con conexión a BigQuery.

## Requisitos previos: CLI de Google Cloud

Este repo incluye una skill de Claude Code que instala y configura `gcloud` paso a paso.
Abre Claude Code en la raíz del proyecto y escribe:

```
/gcloud-cli-install
```

Claude instalará la CLI, te guiará por `gcloud init` y `gcloud auth application-default login`,
habilitará las APIs de BigQuery y Vertex AI, y verificará la conexión antes de lanzar `adk web`.

También puedes usar los scripts directamente:

- macOS / Linux: `bash .claude/skills/gcloud-cli-install/scripts/install.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File .claude\skills\gcloud-cli-install\scripts\install.ps1`
- Verificar todo: `bash .claude/skills/gcloud-cli-install/scripts/verify.sh`

## Agente Text-to-SQL: backend y frontend

- `project_agent_text_to_sql_bigquery/`: agente ADK expuesto como API REST con FastAPI (`main.py`).
  Arranque: `uvicorn project_agent_text_to_sql_bigquery.main:app --reload --port 8080`. Swagger en `/docs`.
- `project_agente_text_to_sql_bigquery_frontend/`: interfaz de chat en React + Vite que consume esa API.
  Arranque: `npm install && npm run dev` dentro de la carpeta. Ver su `README.md`.
