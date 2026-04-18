import React from 'react'
import { useResume } from '../App'
import { levelLabel, levelBadgeClass } from '../utils/helpers'

function matchColor(pct) {
  if (pct >= 78) return '#4E7245'
  if (pct >= 58) return '#9E6F1A'
  return '#9B3A3A'
}

export default function JobMatchCard() {
  const { result: d } = useResume()
  const jobs = d.job_matches || []

  return (
    <div className="space-y-5">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Job Role Matches</h2>
        <p className="text-ink-muted text-sm mt-1">
          Skill overlap + keyword similarity · {d.detected_subfield} · {levelLabel(d.experience_level)}
        </p>
      </div>

      {jobs.length === 0 ? (
        <div className="card p-10 text-center text-ink-muted">
          No job matches found. Try uploading a more detailed resume.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {jobs.map((job, i) => {
            const clr = matchColor(job.match_percent)
            const bg  = job.match_percent >= 78 ? '#F3F6F1' : job.match_percent >= 58 ? '#FAF0D7' : '#FDF4F4'
            return (
              <div key={i} className="card p-5 hover:shadow-card-md transition-shadow">
                {/* Header */}
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div>
                    <h3 className="font-display font-700 text-ink-primary text-base leading-tight">{job.role}</h3>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={`badge ${levelBadgeClass(job.level)} text-[10px]`}>{levelLabel(job.level)}</span>
                      <span className="text-xs text-ink-muted">{job.avg_salary}</span>
                    </div>
                  </div>
                  <div
                    className="text-2xl font-display font-800 flex-shrink-0 px-3 py-1 rounded-xl"
                    style={{ color: clr, background: bg }}
                  >
                    {job.match_percent}%
                  </div>
                </div>

                {/* Bar */}
                <div className="progress-bar h-2 mb-4">
                  <div className="progress-fill h-full" style={{ width: `${job.match_percent}%`, background: clr }} />
                </div>

                {/* Matched skills */}
                {job.matched_skills?.length > 0 && (
                  <div className="mb-3">
                    <span className="text-[10px] font-semibold text-sage-600 uppercase tracking-wide">Matched</span>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {job.matched_skills.slice(0, 5).map((s, j) => (
                        <span key={j} className="skill-chip chip-found text-[10px] px-2 py-0.5">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing skills */}
                {job.missing_skills?.length > 0 && (
                  <div className="mb-3">
                    <span className="text-[10px] font-semibold text-warm-rose uppercase tracking-wide">Missing</span>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {job.missing_skills.slice(0, 4).map((s, j) => (
                        <span key={j} className="skill-chip chip-missing text-[10px] px-2 py-0.5">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Companies */}
                {job.companies?.length > 0 && (
                  <div>
                    <span className="text-[10px] font-semibold text-ink-faint uppercase tracking-wide">Hiring at this level</span>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {job.companies.slice(0, 5).map((c, j) => (
                        <span key={j}
                          className="text-[11px] px-2 py-0.5 rounded-lg bg-stone-50 border border-stone-200 text-stone-600 font-medium">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
