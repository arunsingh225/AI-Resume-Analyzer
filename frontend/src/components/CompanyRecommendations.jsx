import React from 'react'
import { useResume } from '../App'
import { levelLabel } from '../utils/helpers'

const ATS_INFO = {
  high:   { label: 'Strict ATS',   dot: '#9B3A3A', bg: '#FDF4F4', border: '#F2C0C0', tip: 'Needs 70%+ keyword match. Tailor your resume closely.' },
  medium: { label: 'Moderate ATS', dot: '#9E6F1A', bg: '#FAF0D7', border: '#F0D898', tip: 'Standard ATS. Ensure all key sections are present.' },
  low:    { label: 'Flexible ATS', dot: '#4E7245', bg: '#F3F6F1', border: '#C5D4BF', tip: 'More human-led screening. Cover letter matters here.' },
}

function CompanyItem({ co }) {
  const info = ATS_INFO[co.ats_strictness] || ATS_INFO.medium
  return (
    <div className="p-3.5 rounded-xl border transition-all hover:shadow-card"
      style={{ background: '#FAFAF9', borderColor: '#E7E5E4' }}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: info.dot }} />
          <span className="text-sm font-semibold text-ink-primary">{co.name}</span>
        </div>
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0"
          style={{ background: info.bg, color: info.dot, border: `1px solid ${info.border}` }}
        >
          {info.label}
        </span>
      </div>
      {co.preferred_skills?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {co.preferred_skills.slice(0, 3).map((s, i) => (
            <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-stone-100 text-stone-500 font-medium">{s}</span>
          ))}
        </div>
      )}
      <p className="text-[11px] text-ink-muted leading-snug">{info.tip}</p>
    </div>
  )
}

function Section({ title, companies, dotColor, note }) {
  if (!companies?.length) return null
  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-4">
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
        {companies.map((co, i) => <CompanyItem key={i} co={co} />)}
      </div>
    </div>
  )
}

export default function CompanyRecommendations() {
  const { result: d } = useResume()
  const cr = d.company_recommendations || {}
  const level = d.experience_level
  const field = d.detected_subfield

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
          Role-specific for <strong className="text-ink-secondary">{field}</strong> ·{' '}
          {levelLabel(level)} level · ATS strictness shown for each
        </p>
      </div>

      {/* Legend */}
      <div className="card p-4 flex flex-wrap gap-4">
        <span className="text-xs font-semibold text-ink-muted">ATS Strictness Guide:</span>
        {Object.entries(ATS_INFO).map(([k, v]) => (
          <span key={k} className="flex items-center gap-1.5 text-xs text-ink-muted">
            <span className="w-2 h-2 rounded-full" style={{ background: v.dot }} />
            <span className="font-medium" style={{ color: v.dot }}>{v.label}</span>
            <span>— {v.tip}</span>
          </span>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Section
          title="MNCs & Large Firms"
          companies={cr.mncs}
          dotColor="#4B5570"
          note={mnc_note}
        />
        <Section
          title="Startups & Scale-ups"
          companies={cr.startups}
          dotColor="#4E7245"
          note={startup_note}
        />
        <Section
          title="Product Companies"
          companies={cr.product_companies}
          dotColor="#9E6F1A"
          note="Product companies need deep domain knowledge. Ensure your resume shows product thinking and measurable outcomes."
        />
      </div>

      {/* Strategy card */}
      <div className="card p-5" style={{ borderLeft: '3px solid #57534E' }}>
        <h4 className="font-semibold text-ink-primary text-sm mb-2">Application Strategy for {levelLabel(level)}</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-ink-secondary leading-relaxed">
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200">
            <p className="font-semibold text-ink-primary mb-1">Week 1–2</p>
            Apply to Flexible ATS companies first. Use them to build interview confidence and refine your pitch.
          </div>
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200">
            <p className="font-semibold text-ink-primary mb-1">Week 3–4</p>
            Apply to Moderate ATS companies after tailoring your resume with missing keywords from the analysis.
          </div>
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200">
            <p className="font-semibold text-ink-primary mb-1">Week 5+</p>
            Target Strict ATS / MNCs with a polished, tailored resume that scores 70%+ on this ATS checker.
          </div>
        </div>
      </div>
    </div>
  )
}
