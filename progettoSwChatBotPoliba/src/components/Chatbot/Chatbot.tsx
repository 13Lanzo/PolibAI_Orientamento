import { useState, useRef, useEffect, type FormEvent } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { sendMessage, type ChatResponse } from '../../api/chatService'
import './Chatbot.css'

/* ── Types ── */
interface QuickOption {
  label: string
  value: string
}

interface Message {
  text?: string
  htmlText?: string
  sender: 'user' | 'bot'
  timestamp: Date
  type: 'text' | 'map' | 'options' | 'image'
  mapUrl?: string
  mapTitle?: string
  options?: QuickOption[]
}

/* ── SVG icons extracted as tiny components for readability ── */
const LogoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.42 10.922a2 2 0 0 1-.019 1.838L12.83 23h-1.63L2.6 12.76a2 2 0 0 1-.02-1.838L11.19 1h1.64Z"/>
    <path d="m22 10-10 6-10-6 10-6Z"/>
    <path d="M6 12v5c0 2.21 2.69 4 6 4s6-1.79 6-4v-5"/>
  </svg>
)

const ResetIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
    <path d="M3 3v5h5"/>
  </svg>
)

const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" x2="11" y1="2" y2="13"/>
    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
)

const BookIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
  </svg>
)

const SparkleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
  </svg>
)

const InfoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 16v-4"/>
    <path d="M12 8h.01"/>
  </svg>
)

const ChevronRight = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m9 18 6-6-6-6"/>
  </svg>
)

const DownloadIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="download-icon">
    <path d="M12 15V3M12 15L8 11M12 15L16 11M21 21H3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

/* ── Suggestion cards data ── */
const SUGGESTIONS = [
  {
    icon: <LogoIcon />,
    title: 'Corsi di Laurea',
    preview: 'Quali sono i corsi di laurea trienna...',
    text: 'Quali sono i corsi di laurea triennale disponibili?',
  },
  {
    icon: <BookIcon />,
    title: 'Ammissione',
    preview: 'Come funzionano i test di...',
    text: 'Come funzionano i test di ammissione ai corsi di laurea?',
  },
  {
    icon: <SparkleIcon />,
    title: 'Perché Poliba?',
    preview: 'Quali sono i vantaggi di studiare a...',
    text: 'Quali sono i vantaggi di studiare al Politecnico di Bari?',
  },
  {
    icon: <InfoIcon />,
    title: 'Tasse e Borse',
    preview: 'Informazioni su tasse universitarie ...',
    text: 'Quali sono le informazioni riguardo alle tasse universitarie e le borse di studio al Poliba?',
  },
]

/* ═══════════════════════════════════════════
   Chatbot Component
   ═══════════════════════════════════════════ */
export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentInput, setCurrentInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll on new messages / loading change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  /* ── helpers ── */
  const addMessage = (msg: Message) =>
    setMessages(prev => [...prev, msg])

  const parseMarkdown = (raw: string): string => {
    try {
      return DOMPurify.sanitize(marked.parse(raw) as string)
    } catch {
      return raw
    }
  }

  /* ── backend call ── */
  const callBackend = async (text: string) => {
    setIsLoading(true)
    try {
      const response: ChatResponse = await sendMessage(text)
      const parsedHTML = response.response ? parseMarkdown(response.response) : ''
      const injectedOptions = response.options ?? []

      addMessage({
        sender: 'bot',
        timestamp: new Date(),
        type: response.type || 'text',
        text: response.response,
        htmlText: parsedHTML,
        mapUrl: response.mapUrl,
        mapTitle: response.mapTitle,
        options: injectedOptions,
      })
    } catch (err) {
      console.error('Errore backend:', err)
      addMessage({
        text: 'Mi dispiace, non riesco a contattare il server del Poliba in questo momento.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text',
      })
    } finally {
      setIsLoading(false)
    }
  }

  /* ── user actions ── */
  const handleSend = (e?: FormEvent) => {
    e?.preventDefault()
    const text = currentInput.trim()
    if (!text) return
    addMessage({ text, sender: 'user', timestamp: new Date(), type: 'text' })
    setCurrentInput('')
    callBackend(text)
  }

  const handleSuggestion = (text: string) => {
    addMessage({ text, sender: 'user', timestamp: new Date(), type: 'text' })
    callBackend(text)
  }

  const handleOption = (value: string, label: string) => {
    addMessage({ text: `Ho scelto: ${label}`, sender: 'user', timestamp: new Date(), type: 'text' })
    callBackend(value)
  }

  const openMap = (url?: string) => {
    if (url) window.open(url, '_blank')
  }

  const resetChat = () => {
    setMessages([])
    setCurrentInput('')
    setIsLoading(false)
  }

  /* ═══════ RENDER ═══════ */
  return (
    <div className="gemini-app-container">

      {/* ── HEADER ── */}
      <header className="gemini-header">
        <div className="logo-area">
          <div className="logo-icon"><LogoIcon /></div>
          <div className="header-text">
            <h1>Poliba Orientamento AI</h1>
            <h2>ASSISTENTE VIRTUALE UFFICIALE</h2>
          </div>
        </div>
        <div className="header-actions">
          <button className="reset-btn" onClick={resetChat} title="Nuova Conversazione">
            <ResetIcon />
          </button>
        </div>
      </header>

      {/* ── MAIN ── */}
      <main className="gemini-main">

        {/* WELCOME SCREEN */}
        {messages.length === 0 && (
          <div className="welcome-screen">
            <div className="welcome-titles">
              <h2>Benvenuto al <span>Poliba</span></h2>
              <p>Sono qui per aiutarti a scegliere il tuo percorso di studi ideale presso il Politecnico di Bari.</p>
            </div>
            <div className="suggestion-grid">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="suggestion-card" onClick={() => handleSuggestion(s.text)}>
                  <div className="card-icon">{s.icon}</div>
                  <div className="card-text">
                    <h3>{s.title}</h3>
                    <p>{s.preview}</p>
                  </div>
                  <div className="card-arrow"><ChevronRight /></div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* CHAT THREAD */}
        {messages.length > 0 && (
          <div className="chat-thread" ref={scrollRef}>
            {messages.map((msg, idx) => (
              <div key={idx} className={`message-row ${msg.sender === 'user' ? 'user-row' : 'bot-row'}`}>
                <div className={`message-bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}`}>

                  {/* TEXT */}
                  {msg.sender === 'user' && (!msg.type || msg.type === 'text') && (
                    <div className="msg-text">{msg.text}</div>
                  )}
                  {msg.sender === 'bot' && (!msg.type || msg.type === 'text') && (
                    <div
                      className="msg-text markdown-content"
                      dangerouslySetInnerHTML={{ __html: msg.htmlText || msg.text || '' }}
                    />
                  )}

                  {/* IMAGE / INFOGRAPHIC */}
                  {msg.type === 'image' && (
                    <div className="infographic-container">
                      {(msg.htmlText || msg.text) && (
                        <div
                          className="msg-text markdown-content"
                          dangerouslySetInnerHTML={{ __html: msg.htmlText || msg.text || '' }}
                        />
                      )}
                      {msg.mapUrl && (
                        <img src={msg.mapUrl} alt="Infografica Corso" className="generated-infographic" />
                      )}
                      {msg.mapUrl && (
                        <a href={msg.mapUrl} download="infografica_poliba.png" className="download-button">
                          <DownloadIcon />
                          Scarica Infografica
                        </a>
                      )}
                    </div>
                  )}

                  {/* MAP */}
                  {msg.type === 'map' && (
                    <div className="msg-map">
                      <div className="map-title">📍 {msg.mapTitle}</div>
                      <div className="map-img-box" onClick={() => openMap(msg.mapUrl)}>
                        <img src={msg.mapUrl} alt="Mappa" />
                        <div className="map-zoom">🔍 Apri mappa</div>
                      </div>
                      <p className="map-desc">{msg.text}</p>
                    </div>
                  )}

                  {/* OPTIONS */}
                  {msg.options && msg.options.length > 0 && (
                    <div className="msg-options">
                      {msg.type === 'options' && <p>{msg.text}</p>}
                      <div className="options-flex">
                        {msg.options.map((opt, oi) => (
                          <button
                            key={oi}
                            className={`opt-btn ${opt.value.startsWith('INFO_') ? 'infographic-btn' : ''}`}
                            onClick={() => handleOption(opt.value, opt.label)}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              </div>
            ))}

            {/* TYPING INDICATOR */}
            {isLoading && (
              <div className="message-row bot-row">
                <div className="message-bubble bot-bubble typing-bubble">
                  <div className="dot" />
                  <div className="dot" />
                  <div className="dot" />
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* ── FOOTER ── */}
      <footer className="gemini-footer">
        <form className="input-container" onSubmit={handleSend}>
          <input
            type="text"
            value={currentInput}
            onChange={e => setCurrentInput(e.target.value)}
            placeholder="Chiedi informazioni sui corsi, test di ammissione..."
          />
          <button
            type="submit"
            className="send-action-btn"
            disabled={!currentInput.trim() || isLoading}
          >
            <SendIcon />
          </button>
        </form>
        <div className="footer-disclaimer">
          POLITECNICO DI BARI &bull; ORIENTAMENTO UNIVERSITARIO
        </div>
      </footer>

    </div>
  )
}
