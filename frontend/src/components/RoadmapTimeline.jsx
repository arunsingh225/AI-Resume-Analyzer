import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { useResume } from '../App'

const WEEK_COLORS = [
  '#2563EB','#16A34A','#7C3AED','#D97706','#DC2626',
  '#0891B2','#DB2777','#059669','#D97706','#7C3AED','#2563EB','#16A34A',
]

export default function RoadmapTimeline() {
  const { result: d } = useResume()
  const roadmap = d.roadmap || []
  const [expanded, setExpanded] = useState(0)

  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Learning Roadmap</h2>
        <p className="text-ink-muted text-sm mt-1">
          Personalized {roadmap.length}-week plan for {d.detected_subfield} · {d.experience_level} level
        </p>
      </div>

      {/* Mini timeline overview */}
      <div className="card p-5 overflow-x-auto scrollbar-thin">
        <div className="flex gap-2 min-w-max pb-1">
          {roadmap.map((week, i) => (
            <button
              key={i}
              onClick={() => setExpanded(i)}
              className={`flex-shrink-0 flex flex-col items-center gap-1 px-3 py-2 rounded-xl border-2 transition-all ${
                expanded === i
                  ? 'border-brand-500 bg-brand-50'
                  : 'border-surface-border bg-surface-card hover:border-brand-200'
              }`}
            >
              <div
                className="w-6 h-6 rounded-full text-white text-[10px] font-bold flex items-center justify-center"
                style={{ background: WEEK_COLORS[i % WEEK_COLORS.length] }}
              >
                {week.week}
              </div>
              <span className="text-[10px] text-ink-muted max-w-[64px] text-center leading-tight line-clamp-2">
                {week.title}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Expanded week detail */}
      {roadmap.length > 0 && (
        <div className="card p-6 border-l-4" style={{ borderLeftColor: WEEK_COLORS[expanded % WEEK_COLORS.length] }}>
          <div className="flex items-center gap-3 mb-4">
            <div
              className="w-10 h-10 rounded-xl text-white text-base font-bold flex items-center justify-center flex-shrink-0"
              style={{ background: WEEK_COLORS[expanded % WEEK_COLORS.length] }}
            >
              {roadmap[expanded].week}
            </div>
            <div>
              <h3 className="font-display font-700 text-ink-primary">{roadmap[expanded].title}</h3>
              <p className="text-xs text-ink-muted">Week {roadmap[expanded].week} of {roadmap.length}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            {/* Tasks */}
            <div className="sm:col-span-2">
              <h4 className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">Tasks</h4>
              <ul className="space-y-2">
                {(roadmap[expanded].tasks || []).map((task, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <span className="text-brand-600 font-bold mt-0.5">→</span>
                    <span className="text-ink-secondary">{task}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Skills + Resources */}
            <div className="space-y-4">
              {roadmap[expanded].skills?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">Skills</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {roadmap[expanded].skills.map((sk, i) => (
                      <span key={i} className="skill-chip chip-neutral text-[11px]">{sk}</span>
                    ))}
                  </div>
                </div>
              )}
              {roadmap[expanded].resources?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">Resources</h4>
                  <ul className="space-y-1">
                    {roadmap[expanded].resources.map((r, i) => (
                      <li key={i} className="text-xs text-ink-secondary flex gap-1.5">
                        <span className="text-brand-400">•</span>{r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Week navigation */}
          <div className="flex justify-between mt-5 pt-4 border-t border-surface-border">
            <button
              disabled={expanded === 0}
              onClick={() => setExpanded(e => e - 1)}
              className="btn-ghost text-xs disabled:opacity-30"
            >
              ← Previous week
            </button>
            <button
              disabled={expanded === roadmap.length - 1}
              onClick={() => setExpanded(e => e + 1)}
              className="btn-ghost text-xs disabled:opacity-30"
            >
              Next week →
            </button>
          </div>
        </div>
      )}

      {/* All weeks collapsed list */}
      <div className="space-y-2">
        <h3 className="font-display font-600 text-ink-primary text-sm">All weeks at a glance</h3>
        {roadmap.map((week, i) => (
          <button
            key={i}
            onClick={() => setExpanded(i)}
            className={`w-full text-left card p-4 flex items-center gap-4 hover:shadow-card-md transition-all ${expanded === i ? 'ring-2 ring-brand-500' : ''}`}
          >
            <div
              className="w-8 h-8 rounded-lg text-white text-xs font-bold flex items-center justify-center flex-shrink-0"
              style={{ background: WEEK_COLORS[i % WEEK_COLORS.length] }}
            >
              {week.week}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-sm text-ink-primary">{week.title}</div>
              <div className="text-xs text-ink-muted truncate">{week.tasks?.[0]}</div>
            </div>
            <div className="flex flex-wrap gap-1 max-w-[140px] justify-end">
              {(week.skills || []).slice(0, 2).map((sk, j) => (
                <span key={j} className="skill-chip chip-neutral text-[10px] px-2 py-0.5">{sk}</span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
