import React, { useState } from 'react'
import { ExternalLink, Briefcase, ChevronDown, ChevronUp, Linkedin } from 'lucide-react'
import { useResume } from '../App'
import { levelLabel, levelBadgeClass, scoreColor } from '../utils/helpers'

function matchColor(pct) {
  if (pct >= 78) return '#4E7245'
  if (pct >= 55) return '#9E6F1A'
  return '#9B3A3A'
}

function matchBg(pct) {
  if (pct >= 78) return '#F3F6F1'
  if (pct >= 55) return '#FAF0D7'
  return '#FDF4F4'
}

function matchLabel(pct) {
  if (pct >= 85) return { text: 'Excellent Match', emoji: '🌟' }
  if (pct >= 75) return { text: 'Strong Match',    emoji: '✅' }
  if (pct >= 60) return { text: 'Good Match',      emoji: '👍' }
  if (pct >= 45) return { text: 'Partial Match',   emoji: '⚡' }
  return            { text: 'Skill Gap',           emoji: '📈' }
}

function linkedinJobUrl(role, location = 'India') {
  const q = encodeURIComponent(`${role} ${location}`)
  return `https://www.linkedin.com/jobs/search/?keywords=${q}&location=${encodeURIComponent(location)}&f_E=1,2`
}

function linkedinInternUrl(role, location = 'India') {
  const q = encodeURIComponent(`${role} internship`)
  return `https://www.linkedin.com/jobs/search/?keywords=${q}&location=${encodeURIComponent(location)}&f_E=1`
}

function JobCard({ job }) {
  const [expanded, setExpanded] = useState(false)
  const clr   = matchColor(job.match_percent)
  const bg    = matchBg(job.match_percent)
  const label = matchLabel(job.match_percent)

  const shownMatched = expanded ? job.matched_skills : job.matched_skills?.slice(0, 5)
  const shownMissing = expanded ? job.missing_skills  : job.missing_skills?.slice(0, 4)
  const hasMore = (job.matched_skills?.length > 5) || (job.missing_skills?.length > 4)

  return (
    <div className="card p-5 hover:shadow-card-md transition-all duration-200 flex flex-col gap-3">

      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-display font-700 text-ink-primary text-base leading-tight truncate">{job.role}</h3>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <span className={`badge ${levelBadgeClass(job.level)} text-[10px]`}>{levelLabel(job.level)}</span>
            <span className="text-xs text-ink-muted font-medium">{job.avg_salary}</span>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
              style={{ background: bg, color: clr }}>
              {label.emoji} {label.text}
            </span>
          </div>
        </div>
        {/* Match % badge */}
        <div className="text-2xl font-display font-800 flex-shrink-0 px-3 py-1 rounded-xl"
          style={{ color: clr, background: bg }}>
          {job.match_percent}%
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-bar h-2">
        <div className="progress-fill h-full transition-all duration-700"
          style={{ width: `${job.match_percent}%`, background: clr }} />
      </div>

      {/* Skills */}
      <div className="space-y-2.5">
        {shownMatched?.length > 0 && (
          <div>
            <span className="text-[10px] font-bold text-sage-600 uppercase tracking-wider">✓ Matched Skills</span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {shownMatched.map((s, j) => (
                <span key={j} className="skill-chip chip-found text-[10px] px-2 py-0.5">{s}</span>
              ))}
            </div>
          </div>
        )}

        {shownMissing?.length > 0 && (
          <div>
            <span className="text-[10px] font-bold text-warm-rose uppercase tracking-wider">✗ Skills to Gain</span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {shownMissing.map((s, j) => (
                <span key={j} className="skill-chip chip-missing text-[10px] px-2 py-0.5">{s}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Show more/less */}
      {hasMore && (
        <button onClick={() => setExpanded(e => !e)}
          className="flex items-center gap-1 text-[11px] text-ink-muted hover:text-ink-secondary transition-colors self-start">
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          {expanded ? 'Show less' : `Show all skills`}
        </button>
      )}

      {/* Companies */}
      {job.companies?.length > 0 && (
        <div>
          <span className="text-[10px] font-semibold text-ink-faint uppercase tracking-wide">🏢 Hiring Companies</span>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {job.companies.slice(0, 6).map((c, j) => (
              <span key={j}
                className="text-[11px] px-2 py-0.5 rounded-lg bg-stone-50 border border-stone-200 text-stone-600 font-medium">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action tip */}
      <div className="rounded-xl px-3 py-2 text-xs text-ink-muted"
        style={{ background: `${clr}08`, border: `1px solid ${clr}20` }}>
        {job.match_percent >= 75
          ? '🎯 You are a strong candidate — apply now!'
          : job.match_percent >= 55
          ? `💡 Learn ${job.missing_skills?.[0] || 'the missing skills'} to boost your match.`
          : `📚 Upskill in ${job.missing_skills?.slice(0,2).join(' & ') || 'key areas'} to qualify.`}
      </div>

      {/* Apply buttons */}
      <div className="flex gap-2 flex-wrap pt-0.5">
        <a href={linkedinJobUrl(job.role)} target="_blank" rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-semibold
            bg-[#0A66C2] text-white hover:bg-[#004182] transition-colors">
          <ExternalLink size={12} /> Apply — Jobs
        </a>
        <a href={linkedinInternUrl(job.role)} target="_blank" rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-semibold
            border border-[#0A66C2] text-[#0A66C2] hover:bg-[#0A66C2]/5 transition-colors">
          <ExternalLink size={12} /> Apply — Internship
        </a>
      </div>
    </div>
  )
}

export default function JobMatchCard() {
  const { result: d } = useResume()
  const jobs = d.job_matches || []

  return (
    <div className="space-y-5">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Job Role Matches</h2>
        <p className="text-ink-muted text-sm mt-1">
          Skill overlap + keyword similarity · <strong className="text-ink-secondary">{d.detected_subfield}</strong>
          {' · '}{levelLabel(d.experience_level)}
          {' · '}<span className="text-ink-faint">{jobs.length} roles found</span>
        </p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-[11px] text-ink-muted">
        {[
          { color:'#4E7245', label:'≥75% Strong' },
          { color:'#9E6F1A', label:'55–74% Good' },
          { color:'#9B3A3A', label:'<55% Gap'  },
        ].map(({ color, label }) => (
          <span key={label} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: color }} />
            {label}
          </span>
        ))}
      </div>

      {jobs.length === 0 ? (
        <div className="card p-10 text-center text-ink-muted">
          <Briefcase size={32} className="mx-auto mb-3 text-stone-300" />
          No job matches found. Try uploading a more detailed resume.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {jobs.map((job, i) => <JobCard key={i} job={job} />)}
        </div>
      )}
    </div>
  )
}
