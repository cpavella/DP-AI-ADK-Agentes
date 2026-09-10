# Frontend del Agente Text-to-SQL de CitiBike (React + Vite)

Interfaz de chat que consume la API FastAPI del agente definida en
`../project_agent_text_to_sql_bigquery/main.py`.

## Requisitos

- Node.js 20 o superior (`node -v`)
- La API del agente corriendo (ver más abajo)

## Puesta en marcha

1. Levanta la API (desde la raíz del repo, con las credenciales de gcloud ya creadas):

   ```bash
   uvicorn project_agent_text_to_sql_bigquery.main:app --reload --port 8080
   ```

2. Instala dependencias y arranca el frontend (desde esta carpeta):

   ```bash
   npm install
   npm run dev
   ```

3. Abre http://localhost:5173

## Configuración

Copia `.env.example` a `.env` y ajusta `VITE_API_URL` si la API no corre en `http://localhost:8080`.
Si cambias el puerto del frontend, añade su origen a la variable `CORS_ORIGINS` de la API.

## Estructura

```
src/
├── api.js                  # Cliente HTTP: /health, /chat, /sessions
├── App.jsx                 # Estado del chat, sesión y persistencia en localStorage
├── components/
│   ├── Sidebar.jsx         # Logo, estado de la API, nueva conversación, ejemplos
│   ├── MessageList.jsx     # Lista de mensajes e indicador "escribiendo"
│   ├── Message.jsx         # Burbuja con Markdown y el SQL ejecutado (desplegable)
│   └── ChatInput.jsx       # Caja de texto (Enter envía, Shift+Enter salto de línea)
└── index.css               # Estilos
```

## Build de producción

```bash
npm run build      # genera dist/
npm run preview    # sirve dist/ en local para probarlo
```
