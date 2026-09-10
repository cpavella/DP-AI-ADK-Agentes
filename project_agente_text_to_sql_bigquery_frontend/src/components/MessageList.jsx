import Message from './Message.jsx'

export default function MessageList({ messages, loading, bottomRef }) {
  return (
    <section className="messages" aria-live="polite">
      {messages.length === 0 && !loading && (
        <div className="messages__empty">
          <p>Hazme una pregunta sobre los viajes de CitiBike en Nueva York.</p>
          <p className="muted">Yo escribo y ejecuto el SQL en BigQuery por ti.</p>
        </div>
      )}

      {messages.map((m, i) => (
        <Message key={i} message={m} />
      ))}

      {loading && (
        <div className="message message--assistant">
          <div className="message__avatar">🤖</div>
          <div className="message__bubble typing">
            <span /><span /><span />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </section>
  )
}
