import { useEffect, useRef, useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import MessageList from './components/MessageList.jsx'
import ChatInput from './components/ChatInput.jsx'
import { deleteSession, getHealth, sendMessage } from './api.js'

const USER_ID = 'user'
const STORAGE_KEY = 'citibike-agent-session'

// Recupera la sesión guardada en el navegador (si existe) para continuar la conversación tras recargar.
function loadStoredSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { sessionId: null, messages: [] }
  } catch {
    return { sessionId: null, messages: [] }
  }
}

export default function App() {
  const [{ sessionId, messages }, setChat] = useState(loadStoredSession)
  const [loading, setLoading] = useState(false)
  const [health, setHealth] = useState({ status: 'checking' })
  const bottomRef = useRef(null)

  // Comprueba la API al arrancar
  useEffect(() => {
    getHealth()
      .then((h) => setHealth({ ...h, status: 'ok' }))
      .catch((e) => setHealth({ status: 'error', error: e.message }))
  }, [])

  // Persiste la conversación en el navegador
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ sessionId, messages }))
    } catch {
      // almacenamiento no disponible
    }
  }, [sessionId, messages])

  // Baja al último mensaje
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend(text) {
    const question = text.trim()
    if (!question || loading) return

    setChat((prev) => ({ ...prev, messages: [...prev.messages, { role: 'user', content: question }] }))
    setLoading(true)

    try {
      const data = await sendMessage({ message: question, sessionId, userId: USER_ID })
      setChat((prev) => ({
        sessionId: data.session_id,
        messages: [
          ...prev.messages,
          { role: 'assistant', content: data.response, sqlQueries: data.sql_queries ?? [], charts: data.charts ?? [] },
        ],
      }))
    } catch (e) {
      setChat((prev) => ({
        ...prev,
        messages: [...prev.messages, { role: 'assistant', content: `⚠️ ${e.message}`, error: true }],
      }))
    } finally {
      setLoading(false)
    }
  }

  async function handleNewConversation() {
    if (sessionId) {
      // Si la sesión ya no existe en el servidor (reinicio), ignoramos el error
      deleteSession(USER_ID, sessionId).catch(() => {})
    }
    setChat({ sessionId: null, messages: [] })
  }

  return (
    <div className="layout">
      <Sidebar health={health} sessionId={sessionId} onNewConversation={handleNewConversation} />

      <main className="chat">
        <header className="chat__header">
          <h1>🤖 Agente Analista de Datos de CitiBike</h1>
          <p>Hecho con Google ADK + FastAPI (backend) y React + Vite (frontend)</p>
        </header>

        <MessageList messages={messages} loading={loading} bottomRef={bottomRef} />

        <ChatInput onSend={handleSend} disabled={loading || health.status !== 'ok'} />
      </main>
    </div>
  )
}
