# tools/run_sql_query.py

from sqlalchemy import create_engine, text
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
import json
from google.adk.tools import ToolContext

# --- Configuración de conexión a BigQuery ---
# Reemplaza con tu propio ID de proyecto de Google Cloud
#TU_PROYECTO_GCP_ID = "project-mlops-10-streamlit" #******************************************************************************
TU_PROYECTO_GCP_ID = "datapath-ai-17-cpai"
# URI de conexión que indica a SQLAlchemy usar BigQuery y la tabla pública de CitiBike
# bigquery://<dataset>/<table>
db_uri = "bigquery://bigquery-public-data/new_york_citibike"

def get_bigquery_connection():
    # Inicializamos el cliente de BigQuery con nuestro proyecto
    client = bigquery.Client(project=TU_PROYECTO_GCP_ID)
    # Creamos y devolvemos la conexión DB-API compatible con SQLAlchemy
    connection = dbapi.connect(client=client)
    return connection

engine = create_engine(db_uri, creator=get_bigquery_connection)
# -----------------------------------------------------------


# Esta es ahora una función de Python normal, al igual que tus herramientas de RAG.
# El ADK la convertirá en una herramienta automáticamente.
# Devuelve Markdown para que el agente pueda mostrarlo en la interfaz de usuario.
# Guarda last_query_rows y last_query_columns en el estado de la sesión para 
# que otras herramientas puedan acceder a los datos sin volver a consultar BigQuery. 
def run_sql_query(query: str, tool_context: ToolContext) -> str:
    """
    Ejecuta una consulta SQL en BigQuery sobre los datos de CitiBike.

    Guarda además el resultado estructurado en el estado de la sesión
    para que otras herramientas, como create_visualization, puedan
    utilizar los datos sin volver a consultar BigQuery.

    Args:
        query: Consulta SQL completa compatible con BigQuery.

    Returns:
        Resultado de la consulta como tabla Markdown o mensaje de error.
    """

    # Limpiar resultados anteriores para evitar usar datos viejos
    tool_context.state["last_query_rows"] = []
    tool_context.state["last_query_columns"] = []

    try:
        with engine.connect() as connection:
            result_proxy = connection.execute(text(query))

            df = pd.DataFrame(
                result_proxy.fetchall(),
                columns=result_proxy.keys()
            )

            if df.empty:
                return (
                    "La consulta se ejecutó correctamente, "
                    "pero no devolvió resultados."
                )

            # Guardamos como máximo 100 filas para visualización
            df_chart = df.head(100)

            # Conversión segura a JSON
            rows = json.loads(
                df_chart.to_json(
                    orient="records",
                    date_format="iso"
                )
            )

            tool_context.state["last_query_rows"] = rows
            tool_context.state["last_query_columns"] = list(df.columns)
            tool_context.state["last_query_row_count"] = len(df)

            # Se mantiene el comportamiento actual
            return df.to_markdown(index=False)

    except Exception as e:

        tool_context.state["last_query_rows"] = []
        tool_context.state["last_query_columns"] = []

        return f"Error al ejecutar la consulta: {e}"