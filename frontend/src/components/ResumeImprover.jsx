import React, { useState } from 'react'
import { useResume } from '../App'
import { improveResume } from '../services/api'
import { Wand2, CheckCircle2, ArrowRight, Lightbulb, AlertTriangle } from 'lucide-react'

export default function ResumeImprover() {
  const { result } = useResume()
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [tab,     setTab]     = useState('bullets')   // bullets | summary | sections | tips

  const handleImprove = async () => {
    if (!result?.raw_text_preview) { setError('Please analyze a resume first.'); return }
    setError(''); setLoading(true)
    try {
      const text = result.raw_text_preview
      const res  = await improveResume(text)
      setData(res)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Improvement analysis failed')
    } finally { setLoading(false) }
  }

  if (!data) return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Resume Improver</h2>
        <p className="text-ink-muted text-sm mt-1">
          AI-powered rule-based engine to improve bullet points, wording, and structure
        </p>
      </div>
      <div className="card p-8 text-center">
        <div className="w-16 h-16 rounded-3xl bg-stone-100 flex items-center justify-center mx-auto mb-5">
          <Wand2 size={28} className="text-stone-500" />
        </div>
        <h3 className="font-display font-700 text-ink-primary text-lg mb-2">Improve Your Resume</h3>
        <p className="text-ink-secondary text-sm mb-6 max-w-sm mx-auto leading-relaxed">
          Get specific suggestions to strengthen your bullet points, fix weak phrasing,
          and improve every section of your resume.
        </p>
        {error && <p className="text-warm-rose text-sm mb-4">{error}</p>}
        <button onClick={handleImprove} disabled={loading}
          className="btn-primary px-8 py-3 inline-flex items-center gap-2 mx-auto disabled:opacity-60">
          {loading
            ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Analyzing…</>
            : <><Wand2 size={15} />Improve My Resume</>}
        </button>
      </div>
    </div>
  )

  const changed = data.improved_bullets?.filter(b => b.changed) || []

  return (
    <div className="space-y-5 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-700 text-ink-primary">Resume Improvements</h2>
          <p className="text-ink-muted text-sm mt-1">
            {data.stats.bullets_improved} bullets improved · {Object.keys(data.section_suggestions).length} section issues found
          </p>
        </div>
        <button onClick={() => setData(null)} className="btn-ghost text-xs py-2">Re-analyze</button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Bullets Improved', value: data.stats.bullets_improved, color: '#4E7245' },
          { label: 'Total Analyzed',   value: data.stats.total_bullets,    color: '#57534E' },
          { label: 'Section Issues',   value: Object.keys(data.section_suggestions).length, color: '#9E6F1A' },
        ].map(({ label, value, color }) => (
          <div key={label} className="stat-card text-center">
            <div className="text-2xl font-display font-700 mb-1" style={{ color }}>{value}</div>
            <div className="text-xs text-ink-muted">{label}</div>
          </div>
        ))}
      </div>

      {/* Tab nav */}
      <div className="flex bg-stone-100 rounded-xl p-1 gap-1">
        {[
          { id: 'bullets',  label: 'Bullet Points' },
          { id: 'summary',  label: 'Summary' },
          { id: 'sections', label: 'Sections' },
          { id: 'tips',     label: 'Overall Tips' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all ${tab === t.id ? 'bg-white shadow-card text-ink-primary' : 'text-ink-muted hover:text-ink-secondary'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Bullets tab */}
      {tab === 'bullets' && (
        <div className="space-y-3">
          {data.improved_bullets?.length ? data.improved_bullets.map((b, i) => (
            <div key={i} className="card p-4">
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 flex-shrink-0 ${b.changed ? 'text-sage-600' : 'text-stone-300'}`}>
                  {b.changed ? <CheckCircle2 size={15} /> : <div className="w-3.5 h-3.5 rounded-full border-2 border-stone-200 mt-0.5" />}
                </div>
                <div className="flex-1 min-w-0">
                  {b.changed ? (
                    <>
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className="text-[10px] font-semibold text-warm-rose uppercase tracking-wide">Before</span>
                        {b.reason && b.reason !== 'No change needed' && (
                          <span className="text-[10px] text-ink-faint bg-stone-50 px-2 py-0.5 rounded border border-stone-200">{b.reason}</span>
                        )}
                      </div>
                      <p className="text-xs text-ink-muted line-through mb-2 leading-relaxed">{b.original}</p>
                      <span className="text-[10px] font-semibold text-sage-600 uppercase tracking-wide">After</span>
                      <p className="text-sm text-ink-primary leading-relaxed mt-1 font-medium">{b.improved}</p>
                      {b.quant_hint && (
                        <div className="flex gap-1.5 mt-2 p-2 bg-warm-amber-bg rounded-lg border border-warm-amber-border">
                          <Lightbulb size={11} className="text-warm-amber mt-0.5 flex-shrink-0" />
                          <p className="text-[11px] text-warm-amber">{b.quant_hint}</p>
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="text-sm text-ink-secondary">{b.original} <span className="text-xs text-sage-400 ml-2">✓ Good</span></p>
                  )}
                </div>
              </div>
            </div>
          )) : <div className="card p-6 text-center text-ink-muted text-sm">No bullet points detected in resume preview.</div>}
        </div>
      )}

      {/* Summary tab */}
      {tab === 'summary' && data.summary_improvement && (
        <div className="space-y-4">
          <div className="card p-5">
            <h3 className="font-display font-600 text-ink-primary text-sm mb-3">Original Summary</h3>
            <p className="text-sm text-ink-secondary leading-relaxed bg-stone-50 p-3 rounded-xl border border-stone-200">
              {data.summary_improvement.original || 'No summary detected.'}
            </p>
          </div>
          <div className="card p-5">
            <h3 className="font-display font-600 text-ink-primary text-sm mb-3 text-sage-700">Improved Summary</h3>
            <p className="text-sm text-ink-primary leading-relaxed bg-sage-50 p-3 rounded-xl border border-sage-200">
              {data.summary_improvement.improved}
            </p>
          </div>
          {data.summary_improvement.suggestions?.length > 0 && (
            <div className="card p-5">
              <h3 className="font-display font-600 text-ink-primary text-sm mb-3">Suggestions</h3>
              <ul className="space-y-2">
                {data.summary_improvement.suggestions.map((s, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <ArrowRight size={13} className="text-warm-amber mt-0.5 flex-shrink-0" />
                    <span className="text-ink-secondary">{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Sections tab */}
      {tab === 'sections' && (
        <div className="space-y-4">
          {Object.entries(data.section_suggestions).length ? Object.entries(data.section_suggestions).map(([sec, tips]) => (
            <div key={sec} className="card p-5">
              <h3 className="font-display font-600 text-ink-primary text-sm mb-3 flex items-center gap-2">
                <AlertTriangle size={14} className="text-warm-amber" />{sec}
              </h3>
              <ul className="space-y-2">
                {tips.map((t, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <ArrowRight size={13} className="text-warm-amber mt-0.5 flex-shrink-0" />
                    <span className="text-ink-secondary">{t}</span>
                  </li>
                ))}
              </ul>
            </div>
          )) : (
            <div className="card p-6 text-center">
              <CheckCircle2 size={24} className="text-sage-500 mx-auto mb-2" />
              <p className="text-ink-secondary text-sm">No major section issues detected.</p>
            </div>
          )}
        </div>
      )}

      {/* Tips tab */}
      {tab === 'tips' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {data.overall_tips.map((tip, i) => (
            <div key={i} className="card p-4 flex gap-3">
              <span className="text-sm font-bold text-stone-400 flex-shrink-0 w-5">{i+1}</span>
              <p className="text-sm text-ink-secondary leading-relaxed">{tip}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
