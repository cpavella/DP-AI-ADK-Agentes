import { useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('')

  function submit(e) {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSend(value)
    setValue('')
  }

  function onKeyDown(e) {
    // Enter envía, Shift+Enter hace salto de línea
    if (e.key === 'Enter' && !e.shiftKey) submit(e)
  }

  return (
    <form className="chat-input" onSubmit={submit}>
      <textarea
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="¿En qué te puedo ayudar?"
        disabled={disabled}
        aria-label="Escribe tu pregunta"
      />
      <button type="submit" className="btn" disabled={disabled || !value.trim()}>
        Enviar
      </button>
    </form>
  )
}
