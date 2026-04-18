import React from 'react'
import { CheckCircle2, AlertTriangle, Lightbulb } from 'lucide-react'
import { useResume } from '../App'

export default function StrengthsWeaknesses() {
  const { result: d } = useResume()
  const sw = d.strengths_weaknesses || {}
  const strengths = sw.strengths || []
  const weaknesses = sw.weaknesses || []
  const recs = sw.recommendations || []

  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Strengths & Weaknesses</h2>
        <p className="text-ink-muted text-sm mt-1">
          Field-specific analysis for {d.detected_subfield}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Strengths */}
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary mb-4 flex items-center gap-2">
            <CheckCircle2 size={18} className="text-status-green" />
            Strengths ({strengths.length})
          </h3>
          {strengths.length === 0 ? (
            <p className="text-ink-muted text-sm">Upload a resume to see strengths.</p>
          ) : (
            <ul className="space-y-3">
              {strengths.map((s, i) => (
                <li key={i} className="flex gap-3 p-3 bg-status-green-bg rounded-xl border border-status-green-ring">
                  <CheckCircle2 size={15} className="text-status-green mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-ink-primary leading-relaxed">{s}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Weaknesses */}
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-status-amber" />
            Areas to Improve ({weaknesses.length})
          </h3>
          {weaknesses.length === 0 ? (
            <p className="text-ink-muted text-sm">No significant weaknesses detected.</p>
          ) : (
            <ul className="space-y-3">
              {weaknesses.map((w, i) => (
                <li key={i} className="flex gap-3 p-3 bg-status-amber-bg rounded-xl border border-status-amber-ring">
                  <AlertTriangle size={15} className="text-status-amber mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-ink-primary leading-relaxed">{w}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {recs.length > 0 && (
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary mb-4 flex items-center gap-2">
            <Lightbulb size={18} className="text-brand-600" />
            Actionable Recommendations
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recs.map((r, i) => (
              <div key={i} className="flex gap-3 p-3 bg-brand-50 rounded-xl border border-brand-100">
                <span className="text-brand-600 font-bold text-sm flex-shrink-0">{String(i + 1).padStart(2, '0')}</span>
                <span className="text-sm text-ink-secondary leading-relaxed">{r}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
