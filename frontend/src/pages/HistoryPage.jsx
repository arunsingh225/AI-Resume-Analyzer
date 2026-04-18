import { useState, useEffect } from 'react'
import { Clock, Trash2, ChevronRight, FileText, Search, Filter, TrendingUp, TrendingDown } from 'lucide-react'
import { getHistory, deleteAnalysis } from '../services/api'
import { useToast } from '../components/ui/Toast'

function ScoreBadge({ score }) {
  const color = score >= 75 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
    : score >= 50 ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
    : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  return <span className={`px-2 py-0.5 rounded-lg text-xs font-bold ${color}`}>{score}</span>
}

function RelativeTime({ dateStr }) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return <span>just now</span>
  if (mins < 60) return <span>{mins}m ago</span>
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return <span>{hrs}h ago</span>
  const days = Math.floor(hrs / 24)
  if (days < 30) return <span>{days}d ago</span>
  return <span>{new Date(dateStr).toLocaleDateString()}</span>
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleting, setDeleting] = useState(null)
  const { addToast } = useToast()

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const data = await getHistory(50, 0)
      setAnalyses(data.analyses || [])
      setTotal(data.total || 0)
    } catch {
      addToast('Failed to load history', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    setDeleting(id)
    try {
      await deleteAnalysis(id)
      setAnalyses(prev => prev.filter(a => a.id !== id))
      setTotal(prev => prev - 1)
      addToast('Analysis deleted', 'success')
    } catch {
      addToast('Failed to delete', 'error')
    } finally {
      setDeleting(null)
    }
  }

  const filtered = analyses.filter(a => {
    if (!search) return true
    const q = search.toLowerCase()
    return (
      (a.candidate_name || '').toLowerCase().includes(q) ||
      (a.detected_field || '').toLowerCase().includes(q) ||
      (a.filename || '').toLowerCase().includes(q)
    )
  })

  const avgScore = analyses.length > 0
    ? Math.round(analyses.reduce((sum, a) => sum + (a.ats_score || 0), 0) / analyses.length)
    : 0

  const bestScore = analyses.length > 0
    ? Math.max(...analyses.map(a => a.ats_score || 0))
    : 0

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-10 space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 rounded-2xl bg-white/60 animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-ink-primary">Analysis History</h1>
          <p className="text-sm text-ink-muted mt-1">
            {total} {total === 1 ? 'analysis' : 'analyses'} saved
          </p>
        </div>

        {/* Stats */}
        {analyses.length > 0 && (
          <div className="flex items-center gap-4">
            <div className="text-center px-4 py-2 rounded-xl bg-white/80 border border-stone-200 dark:bg-stone-800/50 dark:border-stone-700">
              <p className="text-lg font-bold text-ink-primary">{avgScore}</p>
              <p className="text-[10px] text-ink-muted uppercase tracking-wider">Avg Score</p>
            </div>
            <div className="text-center px-4 py-2 rounded-xl bg-white/80 border border-stone-200 dark:bg-stone-800/50 dark:border-stone-700">
              <p className="text-lg font-bold text-emerald-600">{bestScore}</p>
              <p className="text-[10px] text-ink-muted uppercase tracking-wider">Best</p>
            </div>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name, field, or filename..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-stone-200 bg-white/80
            text-sm text-ink-primary placeholder:text-ink-faint
            focus:outline-none focus:ring-2 focus:ring-stone-300 transition-all"
        />
      </div>

      {/* Empty state */}
      {filtered.length === 0 && (
        <div className="text-center py-16">
          <FileText size={48} className="mx-auto text-stone-300 mb-4" />
          <h3 className="font-display font-semibold text-ink-secondary text-lg mb-2">
            {search ? 'No matches found' : 'No analyses yet'}
          </h3>
          <p className="text-sm text-ink-muted">
            {search ? 'Try a different search term.' : 'Upload a resume to get started.'}
          </p>
        </div>
      )}

      {/* Analysis list */}
      <div className="space-y-3">
        {filtered.map((analysis, idx) => {
          const prevScore = idx < filtered.length - 1 ? filtered[idx + 1]?.ats_score : null
          const trend = prevScore !== null ? (analysis.ats_score || 0) - (prevScore || 0) : 0

          return (
            <div
              key={analysis.id}
              className="group flex items-center gap-4 p-4 rounded-2xl
                bg-white/80 border border-stone-200/80 hover:border-stone-300
                dark:bg-stone-800/50 dark:border-stone-700 dark:hover:border-stone-600
                hover:shadow-card-md transition-all duration-200"
            >
              {/* Icon */}
              <div className="w-10 h-10 rounded-xl bg-stone-100 dark:bg-stone-700 flex items-center justify-center flex-shrink-0">
                <FileText size={18} className="text-ink-muted" />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-semibold text-sm text-ink-primary truncate">
                    {analysis.candidate_name || 'Unknown'}
                  </p>
                  {analysis.detected_field && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-stone-100 dark:bg-stone-700 text-ink-muted">
                      {analysis.detected_field}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-ink-faint">
                  <span className="flex items-center gap-1">
                    <Clock size={11} />
                    <RelativeTime dateStr={analysis.created_at} />
                  </span>
                  {analysis.filename && <span className="truncate max-w-[150px]">{analysis.filename}</span>}
                </div>
              </div>

              {/* Score + Trend */}
              <div className="flex items-center gap-2 flex-shrink-0">
                {trend !== 0 && (
                  <span className={`flex items-center gap-0.5 text-[10px] font-medium ${
                    trend > 0 ? 'text-emerald-600' : 'text-red-500'
                  }`}>
                    {trend > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {trend > 0 ? '+' : ''}{trend}
                  </span>
                )}
                <ScoreBadge score={analysis.ats_score || 0} />
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleDelete(analysis.id)}
                  disabled={deleting === analysis.id}
                  className="w-8 h-8 rounded-lg flex items-center justify-center
                    text-ink-faint hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20
                    transition-colors disabled:opacity-50"
                  title="Delete analysis"
                >
                  {deleting === analysis.id
                    ? <div className="w-3 h-3 border-2 border-red-300 border-t-red-500 rounded-full animate-spin" />
                    : <Trash2 size={14} />
                  }
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
