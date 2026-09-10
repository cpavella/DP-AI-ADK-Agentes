// Cliente HTTP para la API FastAPI del agente.
// La URL base se configura en .env con VITE_API_URL (ver .env.example).

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8080').replace(/\/$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      // sin cuerpo JSON
    }
    throw new Error(detail)
  }

  return response.status === 204 ? null : response.json()
}

/** Comprueba que la API esté viva. Devuelve { status, agent, model }. */
export function getHealth() {
  return request('/health')
}

/**
 * Envía una pregunta al agente.
 * @returns {Promise<{session_id: string, user_id: string, response: string, sql_queries: string[]}>}
 */
export function sendMessage({ message, sessionId, userId = 'user' }) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, user_id: userId, session_id: sessionId ?? null }),
  })
}

/** Recupera el historial de una sesión. */
export function getSession(userId, sessionId) {
  return request(`/sessions/${encodeURIComponent(userId)}/${encodeURIComponent(sessionId)}`)
}

/** Borra una sesión en el servidor. */
export function deleteSession(userId, sessionId) {
  return request(`/sessions/${encodeURIComponent(userId)}/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  })
}

export { API_URL }
