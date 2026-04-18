import React, { useState } from 'react'
import { useResume } from '../App'

const TABS = [
  { id: 'found',    label: 'Found',          chipClass: 'chip-found' },
  { id: 'missing',  label: 'Missing Core',   chipClass: 'chip-missing' },
  { id: 'advanced', label: 'Advanced Gap',   chipClass: 'chip-adv' },
  { id: 'dup',      label: 'Duplicates',     chipClass: 'chip-dup' },
]

export default function SkillsPanel() {
  const { result: d } = useResume()
  const [tab, setTab] = useState('found')
  const s = d.skill_analysis

  const dataMap = {
    found:    s.found,
    missing:  s.missing,
    advanced: s.advanced_missing,
    dup:      s.duplicates,
  }
  const chipMap = {
    found: 'chip-found', missing: 'chip-missing', advanced: 'chip-adv', dup: 'chip-dup',
  }

  const stats = [
    { label: 'Found',      value: s.found.length,            color: 'text-status-green', bgColor: 'bg-status-green-bg' },
    { label: 'Missing',    value: s.missing.length,          color: 'text-status-red',   bgColor: 'bg-status-red-bg' },
    { label: 'Adv. Gap',   value: s.advanced_missing.length, color: 'text-status-purple', bgColor: 'bg-status-purple-bg' },
    { label: 'Duplicates', value: s.duplicates.length,        color: 'text-status-amber', bgColor: 'bg-status-amber-bg' },
  ]

  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Skill Analysis</h2>
        <p className="text-ink-muted text-sm mt-1">Field-specific detection for {d.detected_subfield}</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map(({ label, value, color, bgColor }) => (
          <div key={label} className={`rounded-xl p-4 ${bgColor}`}>
            <div className={`text-2xl font-display font-700 ${color}`}>{value}</div>
            <div className="text-xs text-ink-secondary mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="card p-5">
        <div className="flex gap-1 flex-wrap mb-5 bg-surface-base rounded-xl p-1">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex-1 min-w-[100px] ${
                tab === t.id
                  ? 'bg-surface-card shadow-card text-ink-primary'
                  : 'text-ink-muted hover:text-ink-secondary'
              }`}
            >
              {t.label}
              <span className="ml-1.5 text-xs opacity-60">({dataMap[t.id]?.length || 0})</span>
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2 min-h-[80px]">
          {(dataMap[tab] || []).length === 0 ? (
            <div className="text-ink-muted text-sm py-4">
              {tab === 'dup' ? '✓ No duplicate skills detected — well organized!' : 'None in this category.'}
            </div>
          ) : (
            (dataMap[tab] || []).map((skill, i) => (
              <span key={i} className={`skill-chip ${chipMap[tab]}`}>{skill}</span>
            ))
          )}
        </div>
      </div>

      {/* Soft skills found */}
      {s.found_soft?.length > 0 && (
        <div className="card p-5">
          <h3 className="font-display font-600 text-ink-primary mb-3">Soft Skills Detected</h3>
          <div className="flex flex-wrap gap-2">
            {s.found_soft.map((sk, i) => (
              <span key={i} className="skill-chip chip-neutral">{sk}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
