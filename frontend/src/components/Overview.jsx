import React from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronRight, TrendingUp, AlertTriangle } from 'lucide-react'
import { useResume } from '../App'
import { levelLabel, levelBadgeClass, scoreColor, scoreBgColor } from '../utils/helpers'
import { useAnimatedNumber } from '../hooks/useAnimatedNumber'
import ATSRadarChart from './charts/ATSRadarChart'
import SkillBarChart from './charts/SkillBarChart'

const C = 2 * Math.PI * 58

function scoreBg(v) {
  if (v >= 75) return 'rgba(78,114,69,0.08)'
  if (v >= 55) return 'rgba(158,111,26,0.08)'
  return 'rgba(155,58,58,0.08)'
}

function ATSRing({ score }) {
  const color  = scoreColor(score)
  const offset = C - (score / 100) * C
  return (
    <svg width="152" height="152" viewBox="0 0 152 152">
      <circle cx="76" cy="76" r="58" fill="none" stroke="#E7E5E4" strokeWidth="11" />
      <circle
        cx="76" cy="76" r="58" fill="none"
        stroke={color} strokeWidth="11" strokeLinecap="round"
        strokeDasharray={C} strokeDashoffset={offset}
        className="ats-ring-circle"
      />
      <text x="76" y="70" textAnchor="middle" dominantBaseline="middle"
        fontSize="32" fontWeight="700" fill="#1A1917" fontFamily="Syne,sans-serif"
      >{score}</text>
      <text x="76" y="91" textAnchor="middle" dominantBaseline="middle"
        fontSize="11" fill="#78716C" fontFamily="DM Sans,sans-serif"
      >/ 100</text>
    </svg>
  )
}

export default function Overview() {
  const { result: d } = useResume()
  const navigate = useNavigate()
  const ats  = d.ats_score
  const topJob = d.job_matches?.[0]

  const scoreRows = [
    { label: 'Keywords (35%)',    key: 'keyword_score',    clr: '#4E7245' },
    { label: 'Formatting (20%)', key: 'formatting_score', clr: '#57534E' },
    { label: 'Sections (20%)',   key: 'section_score',    clr: '#9E6F1A' },
    { label: 'Experience (15%)', key: 'experience_score', clr: '#4B5570' },
    { label: 'Skills (10%)',     key: 'skill_score',      clr: '#9B3A3A' },
  ]

  return (
    <div className="space-y-5 stagger-enter">

      {/* ── Hero glass card ── */}
      <div className="glass" style={{ padding: 0, overflow: 'hidden' }}>
        {/* Top accent */}
        <div className="h-1 rounded-t-3xl" style={{ background: `linear-gradient(90deg, #D6D3D1, ${scoreColor(ats.total)}, #D6D3D1)` }} />

        <div className="p-6 flex flex-col sm:flex-row items-center gap-6">
          {/* Ring */}
          <div className="flex-shrink-0 score-ring-glow">
            <ATSRing score={ats.total} />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0 text-center sm:text-left">
            <div className="flex items-center gap-2 flex-wrap justify-center sm:justify-start mb-1">
              <h2 className="font-display text-2xl font-700 text-ink-primary">{d.candidate_name}</h2>
              <span className={`badge ${levelBadgeClass(d.experience_level)}`}>{levelLabel(d.experience_level)}</span>
              <span className="badge badge-stone">{d.file_type}</span>
            </div>
            <p className="text-sm text-ink-muted mb-2">
              {d.detected_field} · {d.detected_subfield} · {d.years_experience}y · Confidence {d.field_confidence}%
            </p>
            <p className="text-sm text-ink-secondary leading-relaxed">{ats.interpretation}</p>
          </div>

          {/* Grade badge */}
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center font-display font-800 text-3xl flex-shrink-0"
            style={{ background: scoreBg(ats.total), color: scoreColor(ats.total), border: `1.5px solid ${scoreColor(ats.total)}30` }}
          >
            {ats.grade}
          </div>
        </div>
      </div>

      {/* ── Quick stats ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'ATS Score',    value: ats.total,                        sub: `Grade ${ats.grade}`,                       color: scoreColor(ats.total) },
          { label: 'Skills Found', value: d.skill_analysis.found.length,    sub: `${d.skill_analysis.missing.length} missing`,color: '#57534E' },
          { label: 'Best Match',   value: `${topJob?.match_percent || 0}%`, sub: topJob?.role || '—',                        color: '#4B5570' },
          { label: 'Experience',   value: `${d.years_experience}y`,         sub: levelLabel(d.experience_level),             color: '#9E6F1A' },
        ].map(({ label, value, sub, color }) => (
          <div key={label} className="stat-card stat-card-premium card-hover">
            <p className="text-[11px] font-semibold text-ink-faint uppercase tracking-wide mb-2">{label}</p>
            <p className="text-2xl font-display font-700 mb-0.5 count-up" style={{ color }}>{value}</p>
            <p className="text-xs text-ink-muted truncate">{sub}</p>
          </div>
        ))}
      </div>

      {/* ── Two column ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* ATS breakdown */}
        <div className="card card-hover p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-600 text-ink-primary text-sm">ATS Breakdown</h3>
            <button onClick={() => navigate('/dashboard/ats')}
              className="btn-ghost text-xs py-1 px-2">
              Details <ChevronRight size={12} />
            </button>
          </div>
          <div className="space-y-3">
            {scoreRows.map(({ label, key, clr }) => (
              <div key={key}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-ink-muted">{label}</span>
                  <span className="font-semibold text-ink-primary">{ats[key]}</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${ats[key]}%`, background: clr }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Job matches */}
        <div className="card card-hover p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-600 text-ink-primary text-sm">Top Job Matches</h3>
            <button onClick={() => navigate('/dashboard/jobs')}
              className="btn-ghost text-xs py-1 px-2">
              View all <ChevronRight size={12} />
            </button>
          </div>
          <div className="space-y-3">
            {d.job_matches.slice(0, 4).map((j, i) => (
              <div key={i}>
                <div className="flex justify-between items-baseline mb-1">
                  <span className="text-sm text-ink-primary font-medium truncate max-w-[70%]">{j.role}</span>
                  <span className="text-sm font-bold font-display" style={{ color: scoreColor(j.match_percent) }}>
                    {j.match_percent}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${j.match_percent}%`, background: scoreColor(j.match_percent) }} />
                </div>
                <p className="text-[10px] text-ink-faint mt-0.5">{j.avg_salary}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Visual Charts ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card card-hover p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-3">ATS Score Radar</h3>
          <ATSRadarChart ats={ats} />
        </div>
        <div className="card card-hover p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-3">Skill Distribution</h3>
          <SkillBarChart
            found={d.skill_analysis?.found_core || d.skill_analysis?.found || []}
            missing={d.skill_analysis?.missing || []}
            advanced={d.skill_analysis?.found_advanced || []}
          />
        </div>
      </div>

      {/* ── Strengths / Weaknesses ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-3 flex items-center gap-2">
            <TrendingUp size={14} className="text-sage-600" /> Strengths
          </h3>
          <ul className="space-y-2">
            {d.strengths_weaknesses.strengths.slice(0, 4).map((s, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-sage-600 mt-0.5 flex-shrink-0">✓</span>
                <span className="text-ink-secondary leading-snug">{s}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-3 flex items-center gap-2">
            <AlertTriangle size={14} className="text-warm-amber" /> Areas to Improve
          </h3>
          <ul className="space-y-2">
            {d.strengths_weaknesses.weaknesses.slice(0, 4).map((w, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-warm-amber mt-0.5 flex-shrink-0">!</span>
                <span className="text-ink-secondary leading-snug">{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
