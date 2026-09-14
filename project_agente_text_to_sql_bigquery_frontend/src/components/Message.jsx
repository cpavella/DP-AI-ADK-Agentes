import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import ChartView from './ChartView.jsx'

export default function Message({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message message--${isUser ? 'user' : 'assistant'}${message.error ? ' message--error' : ''}`}>
      <div className="message__avatar">{isUser ? '🧑' : '🤖'}</div>
      <div className="message__bubble">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        )}

        {message.sqlQueries?.length > 0 && (
          <details className="sql">
            <summary>
              Ver SQL ejecutado ({message.sqlQueries.length})
            </summary>
            {message.sqlQueries.map((q, i) => (
              <pre key={i}><code>{q}</code></pre>
            ))}
          </details>
        )}

        {message.charts?.map((chart, index) => (
          <ChartView
            key={index}
            spec={chart}
          />
        ))}
      </div>
    </div>
  )
}
