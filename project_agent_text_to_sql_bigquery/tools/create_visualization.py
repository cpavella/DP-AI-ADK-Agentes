# Esta tool no dibuja el gráfico, sino que devuelve un diccionario JSON con la especificación del gráfico.


from google.adk.tools import ToolContext


VALID_CHART_TYPES = {
    "bar",
    "line",
    "pie",
    "scatter",
    "metric"
}


def create_visualization(
    chart_type: str,
    title: str,
    x_column: str,
    y_columns: list[str],
    tool_context: ToolContext,
) -> dict:
    """
    Crea una especificación de visualización utilizando el resultado
    de la última consulta ejecutada con run_sql_query.

    Args:
        chart_type:
            Tipo de visualización. Valores permitidos:
            bar, line, pie, scatter o metric.

        title:
            Título descriptivo del gráfico.

        x_column:
            Columna utilizada en el eje X.
            Para metric puede enviarse una cadena vacía.

        y_columns:
            Una o varias columnas numéricas a visualizar.

    Returns:
        Diccionario JSON con la especificación del gráfico.
    """

    if chart_type not in VALID_CHART_TYPES:
        return {
            "status": "error",
            "message": f"Tipo de gráfico no permitido: {chart_type}"
        }

    rows = tool_context.state.get("last_query_rows", [])
    columns = tool_context.state.get("last_query_columns", [])

    if not rows:
        return {
            "status": "error",
            "message": "No existen datos de una consulta previa para graficar."
        }

    if chart_type != "metric" and x_column not in columns:
        return {
            "status": "error",
            "message": f"La columna X '{x_column}' no existe."
        }

    for column in y_columns:
        if column not in columns:
            return {
                "status": "error",
                "message": f"La columna Y '{column}' no existe."
            }

    chart = {
        "type": chart_type,
        "title": title,
        "xKey": x_column,
        "yKeys": y_columns,
        "data": rows
    }

    return {
        "status": "success",
        "chart": chart
    }