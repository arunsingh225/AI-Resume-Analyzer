import { useState } from 'react'
import { Star, MessageSquare, Send, X, CheckCircle2, ChevronDown } from 'lucide-react'
import { submitFeedback } from '../../services/api'
import { useToast } from './Toast'

const CATEGORIES = [
  { value: 'general',  label: 'General',         icon: '💬' },
  { value: 'accuracy', label: 'Score Accuracy',   icon: '🎯' },
  { value: 'ui',       label: 'UI / Design',      icon: '🎨' },
  { value: 'feature',  label: 'Feature Request',  icon: '💡' },
  { value: 'bug',      label: 'Bug Report',       icon: '🐛' },
]

function StarRating({ value, onChange }) {
  const [hover, setHover] = useState(0)

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map(star => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(0)}
          className="transition-transform hover:scale-110 active:scale-95"
        >
          <Star
            size={28}
            className={`transition-colors ${
              star <= (hover || value)
                ? 'fill-amber-400 text-amber-400'
                : 'fill-none text-stone-300'
            }`}
          />
        </button>
      ))}
    </div>
  )
}

export default function FeedbackWidget({ analysisId = null, page = null }) {
  const [isOpen, setIsOpen] = useState(false)
  const [rating, setRating] = useState(0)
  const [category, setCategory] = useState('general')
  const [comment, setComment] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const { addToast } = useToast()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (rating === 0) {
      addToast('Please select a rating', 'error')
      return
    }
    setLoading(true)
    try {
      await submitFeedback({
        rating,
        category,
        comment: comment.trim() || null,
        analysis_id: analysisId,
        page,
      })
      setSubmitted(true)
      addToast('Thank you for your feedback!', 'success')
      setTimeout(() => {
        setIsOpen(false)
        setSubmitted(false)
        setRating(0)
        setComment('')
        setCategory('general')
      }, 2000)
    } catch {
      addToast('Failed to submit feedback', 'error')
    } finally {
      setLoading(false)
    }
  }

  // ── Floating trigger button ──
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-full 
          bg-white/90 backdrop-blur-md border border-stone-200/80 shadow-card-lg
          hover:shadow-xl hover:border-stone-300 transition-all duration-200
          text-sm font-medium text-ink-secondary group"
      >
        <MessageSquare size={16} className="text-stone-400 group-hover:text-sage-600 transition-colors" />
        Feedback
      </button>
    )
  }

  // ── Submitted state ──
  if (submitted) {
    return (
      <div className="fixed bottom-6 right-6 z-50 w-80 p-6 rounded-2xl bg-white/95 backdrop-blur-md border border-stone-200 shadow-card-lg animate-slide-up text-center">
        <div className="w-12 h-12 rounded-full bg-warm-sage-bg flex items-center justify-center mx-auto mb-3">
          <CheckCircle2 size={24} className="text-sage-600" />
        </div>
        <h3 className="font-display font-700 text-ink-primary text-lg mb-1">Thank you!</h3>
        <p className="text-sm text-ink-muted">Your feedback helps us improve.</p>
      </div>
    )
  }

  // ── Feedback form ──
  return (
    <div className="fixed bottom-6 right-6 z-50 w-[340px] rounded-2xl bg-white/95 backdrop-blur-md border border-stone-200 shadow-card-lg animate-slide-up overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 pt-4 pb-2">
        <h3 className="font-display font-700 text-ink-primary text-sm">Share Your Feedback</h3>
        <button
          onClick={() => setIsOpen(false)}
          className="w-7 h-7 rounded-lg flex items-center justify-center text-ink-faint hover:text-ink-muted hover:bg-stone-100 transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="px-5 pb-5 space-y-4">
        {/* Star rating */}
        <div>
          <label className="text-xs text-ink-muted font-medium mb-2 block">How would you rate this?</label>
          <StarRating value={rating} onChange={setRating} />
          {rating > 0 && (
            <p className="text-xs text-ink-faint mt-1">
              {rating === 1 ? 'Poor' : rating === 2 ? 'Fair' : rating === 3 ? 'Good' : rating === 4 ? 'Great' : 'Excellent!'}
            </p>
          )}
        </div>

        {/* Category */}
        <div>
          <label className="text-xs text-ink-muted font-medium mb-2 block">Category</label>
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map(cat => (
              <button
                key={cat.value}
                type="button"
                onClick={() => setCategory(cat.value)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all border ${
                  category === cat.value
                    ? 'bg-stone-800 text-white border-stone-800'
                    : 'bg-stone-50 text-ink-muted border-stone-200 hover:border-stone-300'
                }`}
              >
                {cat.icon} {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Comment */}
        <div>
          <label className="text-xs text-ink-muted font-medium mb-2 block">
            Details <span className="text-ink-faint">(optional)</span>
          </label>
          <textarea
            value={comment}
            onChange={e => setComment(e.target.value)}
            placeholder="Tell us more about your experience..."
            rows={3}
            maxLength={1000}
            className="w-full px-3 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 
              text-sm text-ink-primary placeholder:text-ink-faint resize-none
              focus:outline-none focus:ring-2 focus:ring-stone-300 focus:border-transparent
              transition-all"
          />
          {comment.length > 0 && (
            <p className="text-[10px] text-ink-faint text-right mt-0.5">{comment.length}/1000</p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={rating === 0 || loading}
          className="w-full py-2.5 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2
            disabled:opacity-50 disabled:cursor-not-allowed
            bg-stone-800 text-white hover:bg-stone-900 active:scale-[0.98]"
        >
          {loading ? (
            <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
          ) : (
            <>
              <Send size={14} />
              Submit Feedback
            </>
          )}
        </button>
      </form>
    </div>
  )
}
