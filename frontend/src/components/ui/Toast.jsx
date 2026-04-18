import { useState, useCallback, createContext, useContext } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

const ICONS = {
  success: <CheckCircle2 size={16} className="text-sage-600 flex-shrink-0" />,
  error:   <AlertCircle size={16} className="text-warm-rose flex-shrink-0" />,
  info:    <Info size={16} className="text-slate-600 flex-shrink-0" />,
}

const BG = {
  success: 'bg-warm-sage-bg border-warm-sage-border',
  error:   'bg-warm-rose-bg border-warm-rose-border',
  info:    'bg-warm-slate-bg border-warm-slate-border',
}

function ToastItem({ id, message, type = 'info', onClose }) {
  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border shadow-card-lg animate-slide-up max-w-sm ${BG[type]}`}>
      {ICONS[type]}
      <span className="text-sm text-ink-secondary font-medium flex-1">{message}</span>
      <button onClick={() => onClose(id)} className="text-ink-faint hover:text-ink-muted flex-shrink-0">
        <X size={14} />
      </button>
    </div>
  )
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      {/* Toast container */}
      {toasts.length > 0 && (
        <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2">
          {toasts.map(t => (
            <ToastItem key={t.id} {...t} onClose={removeToast} />
          ))}
        </div>
      )}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside ToastProvider')
  return ctx
}
