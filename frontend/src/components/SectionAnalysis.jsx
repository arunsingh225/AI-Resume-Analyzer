import React from 'react'
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import { useResume } from '../App'

export default function SectionAnalysis() {
  const { result: d } = useResume()
  const sections = d.section_scores || []
  const present  = sections.filter(s => s.present).length
  const total    = sections.length

  return (
    <div className="space-y-5 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-700 text-ink-primary">Section Completeness</h2>
          <p className="text-ink-muted text-sm mt-1">{present} of {total} expected sections found</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-display font-700 text-brand-600">{Math.round((present/Math.max(total,1))*100)}%</div>
          <div className="text-xs text-ink-muted">Section score</div>
        </div>
      </div>

      {/* Progress */}
      <div className="card p-4">
        <div className="progress-bar h-3">
          <div className="progress-fill h-full" style={{ width: `${(present/Math.max(total,1))*100}%`, background: present/total >= 0.8 ? '#16A34A' : present/total >= 0.6 ? '#D97706' : '#DC2626' }} />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {sections.map((s, i) => (
          <div key={i} className={`section-card border-l-4 ${s.present ? 'border-l-status-green' : 'border-l-status-red'}`}>
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {s.present
                  ? <CheckCircle2 size={18} className="text-status-green" />
                  : <XCircle     size={18} className="text-status-red" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm text-ink-primary">{s.name}</span>
                  <span className={`badge ${s.present ? 'badge-green' : 'badge-red'} text-[10px]`}>
                    {s.present ? 'Found' : 'Missing'}
                  </span>
                </div>
                <p className="text-xs text-ink-secondary leading-relaxed">{s.feedback}</p>
                {s.suggestions?.length > 0 && s.suggestions.map((sg, j) => (
                  <div key={j} className="flex gap-1.5 mt-1.5">
                    <AlertCircle size={11} className="text-status-amber mt-0.5 flex-shrink-0" />
                    <span className="text-[11px] text-status-amber">{sg}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
