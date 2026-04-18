import React from 'react'
import { useResume } from '../App'

export default function KeywordHighlighter() {
  const { result: d } = useResume()
  const found   = d.keywords_found   || []
  const missing = d.keywords_missing || []
  const total   = found.length + missing.length
  const pct     = total > 0 ? Math.round((found.length / total) * 100) : 0

  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">ATS Keyword Analysis</h2>
        <p className="text-ink-muted text-sm mt-1">
          {found.length} of {total} critical keywords found · {pct}% keyword coverage
        </p>
      </div>

      {/* Coverage bar */}
      <div className="card p-5">
        <div className="flex justify-between text-sm mb-2">
          <span className="font-semibold text-ink-primary">Keyword Coverage</span>
          <span className="font-bold text-brand-600">{pct}%</span>
        </div>
        <div className="progress-bar h-3 mb-3">
          <div
            className="progress-fill h-full"
            style={{
              width: `${pct}%`,
              background: pct >= 70 ? '#16A34A' : pct >= 50 ? '#D97706' : '#DC2626',
            }}
          />
        </div>
        <div className="flex gap-4 text-xs">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-status-green inline-block" />
            <span className="text-ink-secondary">{found.length} found</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-status-red inline-block" />
            <span className="text-ink-secondary">{missing.length} missing</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Found */}
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-status-green" />
            Found Keywords ({found.length})
          </h3>
          {found.length === 0 ? (
            <p className="text-ink-muted text-sm">No matching keywords detected.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {found.map((kw, i) => (
                <span key={i} className="skill-chip chip-found">{kw}</span>
              ))}
            </div>
          )}
        </div>

        {/* Missing */}
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-status-red" />
            Missing Keywords ({missing.length})
          </h3>
          {missing.length === 0 ? (
            <p className="text-ink-secondary text-sm">All critical keywords are present — excellent!</p>
          ) : (
            <>
              <div className="flex flex-wrap gap-2 mb-3">
                {missing.map((kw, i) => (
                  <span key={i} className="skill-chip chip-missing">{kw}</span>
                ))}
              </div>
              <p className="text-xs text-ink-muted mt-2 leading-relaxed">
                Add these keywords naturally throughout your resume — especially in your
                Summary, Skills, and Experience sections — to pass ATS filters.
              </p>
            </>
          )}
        </div>
      </div>

      {/* Tip card */}
      <div className="card p-5 border-l-4 border-l-brand-500 bg-brand-50/40">
        <h4 className="font-semibold text-brand-700 mb-1 text-sm">Pro tip: Tailoring keywords</h4>
        <p className="text-sm text-ink-secondary leading-relaxed">
          For each job you apply to, copy the job description and paste it into a word-frequency tool.
          Add the top 10–15 keywords from the JD into your resume organically.
          ATS systems score your resume against the specific JD — a 70%+ match gets past most filters.
        </p>
      </div>
    </div>
  )
}
