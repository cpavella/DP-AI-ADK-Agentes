import { API_URL } from '../api.js'

export default function Sidebar({ health, sessionId, onNewConversation }) {
  const statusLabel = {
    checking: 'Conectando…',
    ok: `Conectado · ${health.model ?? ''}`,
    error: 'API no disponible',
  }[health.status]

  return (
    <aside className="sidebar">
      <img src="/datapath-logo.png" alt="Datapath" className="sidebar__logo" />
      <h2>Sistema de Consulta a una base de datos</h2>
      <p className="sidebar__author">Desarrollado por Nombre Apellido</p>
      <hr />

      <div className={`status status--${health.status}`}>
        <span className="status__dot" />
        <span>{statusLabel}</span>
      </div>
      {health.status === 'error' && (
        <p className="sidebar__hint">
          ¿Está corriendo la API en <code>{API_URL}</code>?<br />
          <code>uvicorn project_agent_text_to_sql_bigquery.main:app --port 8080</code>
        </p>
      )}

      <button className="btn btn--secondary" onClick={onNewConversation}>
        🗑️ Nueva conversación
      </button>

      {sessionId && (
        <p className="sidebar__session">
          Sesión: <code>{sessionId.slice(0, 8)}…</code>
        </p>
      )}

      <div className="sidebar__examples">
        <h3>Prueba preguntar</h3>
        <ul>
          <li>¿Cuál es la ruta más popular?</li>
          <li>¿Cuántos viajes hicieron los suscriptores en 2016?</li>
          <li>¿Cuál es la duración promedio de un viaje en minutos?</li>
          <li>Top 5 estaciones de inicio con más viajes</li>
        </ul>
      </div>
    </aside>
  )
}
