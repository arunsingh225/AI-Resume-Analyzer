import React, { useState } from 'react'
import { ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
import { useResume } from '../App'
import { levelLabel } from '../utils/helpers'

const ATS_INFO = {
  high:   { label: 'Strict ATS',   dot: '#9B3A3A', bg: '#FDF4F4', border: '#F2C0C0', tip: 'Needs 70%+ keyword match. Tailor your resume closely.' },
  medium: { label: 'Moderate ATS', dot: '#9E6F1A', bg: '#FAF0D7', border: '#F0D898', tip: 'Standard ATS. Ensure all key sections are present.' },
  low:    { label: 'Flexible ATS', dot: '#4E7245', bg: '#F3F6F1', border: '#C5D4BF', tip: 'More human-led screening. Cover letter matters here.' },
}

function CompanyItem({ co, field }) {
  const info = ATS_INFO[co.ats_strictness] || ATS_INFO.medium

  const linkedinJobsUrl   = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(co.name + ' ' + field)}&location=India&f_TPR=r2592000`
  const linkedinInternUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(co.name + ' internship')}&location=India&f_E=1`

  return (
    <div className="p-3.5 rounded-xl border transition-all hover:shadow-card"
      style={{ background: '#FAFAF9', borderColor: '#E7E5E4' }}>

      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: info.dot }} />
          <span className="text-sm font-semibold text-ink-primary truncate">{co.name}</span>
        </div>
        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0"
          style={{ background: info.bg, color: info.dot, border: `1px solid ${info.border}` }}>
          {info.label}
        </span>
      </div>

      {co.preferred_skills?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {co.preferred_skills.slice(0, 4).map((s, i) => (
            <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-stone-100 text-stone-500 font-medium">{s}</span>
          ))}
        </div>
      )}

      <p className="text-[11px] text-ink-muted leading-snug mb-3">{info.tip}</p>

      <div className="flex flex-wrap gap-2">
        <a href={linkedinJobsUrl} target="_blank" rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg transition-all hover:opacity-80"
          style={{ background: '#0077B5', color: '#fff' }}>
          <ExternalLink size={10} /> Jobs
        </a>
        <a href={linkedinInternUrl} target="_blank" rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg transition-all hover:opacity-80"
          style={{ background: '#E8F4FD', color: '#0077B5', border: '1px solid #B3D4E8' }}>
          <ExternalLink size={10} /> Internship
        </a>
        {co.apply_link && (
          <a href={co.apply_link} target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg transition-all hover:opacity-80"
            style={{ background: '#F5F4F2', color: '#78716C', border: '1px solid #E7E5E4' }}>
            <ExternalLink size={10} /> Careers
          </a>
        )}
      </div>
    </div>
  )
}

const INITIAL_SHOW = 8   // companies visible before "Show more"

function Section({ title, companies, dotColor, note, field }) {
  const [showAll, setShowAll] = useState(false)
  if (!companies?.length) return null

  const visible = showAll ? companies : companies.slice(0, INITIAL_SHOW)
  const remaining = companies.length - INITIAL_SHOW

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-2.5 h-2.5 rounded-full" style={{ background: dotColor }} />
        <h3 className="font-display font-600 text-ink-primary text-sm">{title}</h3>
        <span className="text-xs text-ink-muted">({companies.length})</span>
      </div>
      {note && (
        <p className="text-xs text-ink-muted mb-3 leading-relaxed bg-stone-50 px-3 py-2 rounded-lg border border-stone-200">
          {note}
        </p>
      )}
      <div className="space-y-2.5">
        {visible.map((co, i) => <CompanyItem key={i} co={co} field={field} />)}
      </div>

      {companies.length > INITIAL_SHOW && (
        <button
          onClick={() => setShowAll(s => !s)}
          className="mt-3 w-full flex items-center justify-center gap-1.5 text-xs font-semibold py-2 rounded-xl transition-all hover:opacity-80"
          style={{ background: '#F5F4F2', color: '#57534E', border: '1px solid #E7E5E4' }}
        >
          {showAll
            ? <><ChevronUp size={13} /> Show less</>
            : <><ChevronDown size={13} /> Show {remaining} more companies</>
          }
        </button>
      )}
    </div>
  )
}

export default function CompanyRecommendations() {
  const { result: d } = useResume()
  const cr    = d.company_recommendations || {}
  const level = d.experience_level
  const field = d.detected_subfield

  const total = (cr.mncs?.length || 0) + (cr.startups?.length || 0) + (cr.product_companies?.length || 0)

  const mnc_note = level === 'fresher' || level === 'junior'
    ? `As a ${levelLabel(level)}, focus on MNC training programs. These companies offer structured onboarding and learning budgets.`
    : `At ${levelLabel(level)} level, MNCs look for demonstrable impact and leadership. Highlight metrics in your resume.`

  const startup_note = level === 'fresher' || level === 'junior'
    ? 'Startups offer faster growth and broader exposure. Your resume needs to show initiative and project-driven thinking.'
    : 'Startups at your level value ownership and end-to-end thinking. Emphasize cross-functional work and scale.'

  return (
    <div className="space-y-5">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Company Recommendations</h2>
        <p className="text-ink-muted text-sm mt-1">
          <span className="font-semibold text-ink-secondary">{total} companies</span> curated for{' '}
          <strong className="text-ink-secondary">{field}</strong> · {levelLabel(level)} level ·{' '}
          Click <span className="font-semibold" style={{ color: '#0077B5' }}>Jobs</span> or{' '}
          <span className="font-semibold" style={{ color: '#0077B5' }}>Internship</span> to apply on LinkedIn
        </p>
      </div>

      {/* Legend */}
      <div className="card p-4 flex flex-wrap gap-4">
        <span className="text-xs font-semibold text-ink-muted">ATS Strictness:</span>
        {Object.entries(ATS_INFO).map(([k, v]) => (
          <span key={k} className="flex items-center gap-1.5 text-xs text-ink-muted">
            <span className="w-2 h-2 rounded-full" style={{ background: v.dot }} />
            <span className="font-medium" style={{ color: v.dot }}>{v.label}</span>
            <span>— {v.tip}</span>
          </span>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Section title="MNCs & Large Firms"    companies={cr.mncs}              dotColor="#4B5570" note={mnc_note}     field={field} />
        <Section title="Startups & Scale-ups"  companies={cr.startups}          dotColor="#4E7245" note={startup_note} field={field} />
        <Section title="Product Companies"     companies={cr.product_companies} dotColor="#9E6F1A"
          note="Product companies need deep domain knowledge. Ensure your resume shows product thinking and measurable outcomes."
          field={field} />
      </div>

      {/* Strategy card */}
      <div className="card p-5" style={{ borderLeft: '3px solid #57534E' }}>
        <h4 className="font-semibold text-ink-primary text-sm mb-2">Application Strategy for {levelLabel(level)}</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-ink-secondary leading-relaxed">
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200">
            <p className="font-semibold text-ink-primary mb-1">Week 1–2</p>
            Start with Flexible ATS companies. Apply via LinkedIn Internship links to build confidence and get early calls.
          </div>
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200">
            <p className="font-semibold text-ink-primary mb-1">Week 3–4</p>
            Apply to Moderate ATS startups and product companies after adding missing keywords from your ATS analysis.
          </div>
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200">
            <p className="font-semibold text-ink-primary mb-1">Week 5+</p>
            Target Strict ATS MNCs (Google, Amazon, Flipkart) with a polished resume scoring 70%+ on this checker.
          </div>
        </div>
      </div>
    </div>
  )
}
