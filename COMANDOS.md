# Primer paso
- gcloud init

# Segundo paso
- Construimos el proyecto dentro de la carpeta SRC
- gcloud auth application-default login
- pip install -r requirements.txt
- Lanzamos "adk web"

# Tercer paso: Habilitamos el API de VertexAI
- gcloud services enable aiplatform.googleapis.com --project=project-mlops-10-streamlit

# Cuarto paso: Habilitamos la API de BigQuery


# Cuando quiero hacer la parte de Frontend o Desplegar (Deployar) la aplicación
adk api_server --host 0.0.0.0 --port 8000




adk web