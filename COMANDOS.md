# Crea un Virtual Environment
conda create -n DP-ADK-Agentes python=3.13
# Actiava el Virtual Environment
conda activate DP-ADK-Agentes
# Instala las dependencias:
- pip install -r requirements.txt

# Primer paso
- gcloud init

# Segundo paso: Habilitamos el API de VertexAI y BigQuery
- gcloud services enable aiplatform.googleapis.com bigquery.googleapis.com --project=<TU_PROJECT_ID>

# Para tus programas: el ADK, google-cloud-bigquery, cualquier librería de Google
- gcloud auth application-default login
- gcloud auth application-default set-quota-project <TU_PROJECT_ID>

# Playground de ADK
- adk web

# Cuando quiero hacer la parte de Frontend o Desplegar (Deployar) la aplicación
adk api_server --host 0.0.0.0 --port 8000



# ==============================================================
# ==============================================================
# Crear Histórico de Conversación:
 # Objetivo: guardar las sesiones del agente (historial de conversación) en un
# PostgreSQL gestionado en Cloud SQL, compartido por `adk web` y la API FastAPI.
# Reemplaza <TU_PROJECT_ID> por tu proyecto y <CONTRASEÑA> por una contraseña propia.
# Aviso de coste: Cloud SQL no tiene capa gratuita. La instancia mínima cuesta ~8-10 USD/mes encendida.

# --- 1. Habilitar la API de Cloud SQL
gcloud services enable sqladmin.googleapis.com --project=<TU_PROJECT_ID>

# --- 2. Crear la instancia PostgreSQL (tarda 5-10 minutos). Misma región que Vertex AI.
gcloud sql instances create adk-sessions \
  --project=<TU_PROJECT_ID> \
  --database-version=POSTGRES_16 \
  --edition=ENTERPRISE \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=HDD \
  --storage-size=10GB

# Ver el estado (debe decir RUNNABLE):
gcloud sql instances list --project=<TU_PROJECT_ID>

# --- 3. Crear la base de datos y el usuario que usará el agente
gcloud sql databases create adk_sessions --instance=adk-sessions --project=<TU_PROJECT_ID>
gcloud sql users create adk --instance=adk-sessions --project=<TU_PROJECT_ID> --password='<CONTRASEÑA>'

# --- 4. Instalar el Cloud SQL Auth Proxy (túnel seguro desde tu PC, se autentica con tus ADC)
# macOS:
brew install cloud-sql-proxy
# Linux:
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.14.0/cloud-sql-proxy.linux.amd64 && chmod +x cloud-sql-proxy && sudo mv cloud-sql-proxy /usr/local/bin/
# Windows: descargar https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.14.0/cloud-sql-proxy.x64.exe

# Obtener el "connection name" de la instancia (formato proyecto:region:instancia):
gcloud sql instances describe adk-sessions --project=<TU_PROJECT_ID> --format="value(connectionName)"

# --- 5. Levantar el proxy (dejarlo corriendo en una terminal aparte). Expone la base en localhost:5432
cloud-sql-proxy <TU_PROJECT_ID>:us-central1:adk-sessions --port 5432

# --- 6. Driver de PostgreSQL para Python (ya está en requirements.txt)
pip install asyncpg

# --- 7. Variable de entorno en project_agent_text_to_sql_bigquery/.env  (NO commitear el .env)
# SESSION_DB_URL=postgresql+asyncpg://adk:<CONTRASEÑA>@127.0.0.1:5432/adk_sessions
# Si SESSION_DB_URL no está definida, la API usa SQLite local en .adk/api_sessions.db

# --- 8. Probar con adk web usando la misma base (desde la raíz del repo, con el proxy corriendo)
adk web --session_service_uri="postgresql+asyncpg://adk:<CONTRASEÑA>@127.0.0.1:5432/adk_sessions"

# --- 9. Probar con la API FastAPI (lee SESSION_DB_URL del .env)
uvicorn project_agent_text_to_sql_bigquery.main:app --reload --port 8080



# --- 10. Ver las tablas que el ADK creó solo (sessions, events, app_states, user_states)
# Cliente psql: macOS `brew install libpq && brew link --force libpq`; Linux `sudo apt-get install postgresql-client`
psql "host=127.0.0.1 port=5432 dbname=adk_sessions user=adk"
#   \dt
#   SELECT id, user_id, update_time FROM sessions ORDER BY update_time DESC;
#   SELECT session_id, author, timestamp FROM events ORDER BY timestamp DESC LIMIT 10;
#   \q

# --- Apagar la instancia entre clases (solo se paga el disco) y volver a encenderla
gcloud sql instances patch adk-sessions --project=<TU_PROJECT_ID> --activation-policy=NEVER
gcloud sql instances patch adk-sessions --project=<TU_PROJECT_ID> --activation-policy=ALWAYS

# --- Eliminar la instancia al terminar el curso (borra todo el histórico)
gcloud sql instances delete adk-sessions --project=<TU_PROJECT_ID>


# ==============================================================
# ==============================================================
# Frontend React + Vite (carpeta project_agente_text_to_sql_bigquery_frontend)
# Requiere Node 20+. Con la API corriendo en el puerto 8080:
cd project_agente_text_to_sql_bigquery_frontend
npm install
npm run dev          # abre http://localhost:5173
npm run build        # build de producción en dist/