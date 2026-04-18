import React, { useEffect, useRef } from 'react'
import { useResume } from '../App'
import { scoreColor, scoreBgColor as scoreBg } from '../utils/helpers'
import { useAnimatedNumber } from '../hooks/useAnimatedNumber'
import ATSRadarChart from './charts/ATSRadarChart'

const C = 2 * Math.PI * 80

const SCORE_ROWS = [
  { label: 'Keyword Relevance',    key: 'keyword_score',    weight: '35%', clr: '#4E7245',  desc: 'How well your resume matches critical field-specific ATS keywords' },
  { label: 'Formatting Quality',   key: 'formatting_score', weight: '20%', clr: '#57534E',  desc: 'Contact info, bullet points, action verbs, quantified achievements' },
  { label: 'Section Completeness', key: 'section_score',    weight: '20%', clr: '#9E6F1A',  desc: 'Presence and completeness of expected resume sections for your field' },
  { label: 'Experience Quality',   key: 'experience_score', weight: '15%', clr: '#4B5570',  desc: 'Years of experience, quantified results, leadership, scope of work' },
  { label: 'Skill Coverage',       key: 'skill_score',      weight: '10%', clr: '#9B3A3A',  desc: 'Coverage of core and advanced skills expected for this exact role' },
]

export default function ATSScoreCard() {
  const { result: d } = useResume()
  const ats = d.ats_score
  const ringRef = useRef(null)

  useEffect(() => {
    if (!ringRef.current) return
    const offset = C - (ats.total / 100) * C
    setTimeout(() => { if (ringRef.current) ringRef.current.style.strokeDashoffset = offset }, 120)
  }, [ats.total])

  return (
    <div className="space-y-5">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">ATS Score Analysis</h2>
        <p className="text-ink-muted text-sm mt-1">
          Formula: Keywords 35% · Formatting 20% · Sections 20% · Experience 15% · Skills 10%
          <span className="ml-2 badge badge-stone text-[10px]">{d.detected_subfield}</span>
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

        {/* ── Glass ring card ── */}
        <div className="lg:col-span-2 glass flex flex-col items-center py-8 px-6">
          <svg width="200" height="200" viewBox="0 0 200 200">
            {/* Outer decorative ring */}
            <circle cx="100" cy="100" r="90" fill="none" stroke="#F0EEEC" strokeWidth="1" />
            {/* Track */}
            <circle cx="100" cy="100" r="80" fill="none" stroke="#E7E5E4" strokeWidth="13" />
            {/* Fill */}
            <circle
              ref={ringRef}
              cx="100" cy="100" r="80" fill="none"
              stroke={scoreColor(ats.total)} strokeWidth="13" strokeLinecap="round"
              strokeDasharray={C} strokeDashoffset={C}
              className="ats-ring-circle"
            />
            {/* Inner score */}
            <text x="100" y="92" textAnchor="middle" dominantBaseline="middle"
              fontSize="46" fontWeight="700" fill="#1A1917" fontFamily="Syne,sans-serif"
            >{ats.total}</text>
            <text x="100" y="118" textAnchor="middle" dominantBaseline="middle"
              fontSize="13" fontWeight="600" fill={scoreColor(ats.total)} fontFamily="Syne,sans-serif"
            >Grade {ats.grade}</text>
          </svg>

          {/* Grade box */}
          <div
            className="w-full mt-4 py-3 px-5 rounded-2xl text-center"
            style={{ background: scoreBg(ats.total), border: `1px solid ${scoreColor(ats.total)}25` }}
          >
            <p className="text-sm font-medium text-ink-secondary leading-relaxed">{ats.interpretation}</p>
          </div>

          {/* Improvement tip */}
          {ats.total < 75 && (
            <div className="w-full mt-3 py-3 px-4 rounded-xl bg-stone-50 border border-stone-200">
              <p className="text-xs font-semibold text-ink-secondary mb-1">Quick win to improve score:</p>
              <p className="text-xs text-ink-muted leading-relaxed">
                {ats.keyword_score < 60
                  ? 'Add more field-specific keywords to your Summary and Skills sections.'
                  : ats.formatting_score < 60
                  ? 'Add bullet points with action verbs and quantified achievements.'
                  : ats.section_score < 70
                  ? 'Add missing sections like Certifications or Projects.'
                  : 'Quantify your achievements with numbers, percentages, or revenue impact.'}
              </p>
            </div>
          )}
        </div>

        {/* ── Breakdown ── */}
        <div className="lg:col-span-3 card p-6">
          <h3 className="font-display font-600 text-ink-primary mb-5">Component Breakdown</h3>
          <div className="space-y-5">
            {SCORE_ROWS.map(({ label, key, weight, clr, desc }) => (
              <div key={key}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: clr }} />
                    <span className="text-sm text-ink-secondary font-medium">{label}</span>
                    <span className="text-[10px] text-ink-faint bg-stone-100 px-1.5 py-0.5 rounded font-medium">{weight}</span>
                  </div>
                  <span className="text-sm font-bold font-display text-ink-primary">{ats[key]}</span>
                </div>
                <div className="progress-bar h-2 mb-1.5">
                  <div className="progress-fill h-full" style={{ width: `${ats[key]}%`, background: clr }} />
                </div>
                <p className="text-[11px] text-ink-faint leading-snug">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── What is missing ── */}
      {d.keywords_missing?.length > 0 && (
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-3">
            Top Missing Keywords — Add these to boost your ATS score
          </h3>
          <div className="flex flex-wrap gap-2">
            {d.keywords_missing.slice(0, 16).map((kw, i) => (
              <span key={i} className="skill-chip chip-missing">{kw}</span>
            ))}
          </div>
          <p className="text-xs text-ink-muted mt-3 leading-relaxed">
            Add these keywords naturally in your Summary, Skills, or Experience sections.
            ATS systems perform exact keyword matching — phrasing matters.
          </p>
        </div>
      )}
    </div>
  )
}
