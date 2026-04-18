import React from 'react'
import { ExternalLink, Star } from 'lucide-react'
import { useResume } from '../App'
import { platformBadgeStyle } from '../utils/helpers'

export default function CourseCard() {
  const { result: d } = useResume()
  const courses = d.course_recommendations || []

  const LEVEL_CLASS = {
    Beginner:     'badge-green',
    Intermediate: 'badge-amber',
    Advanced:     'badge-red',
  }

  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Course Recommendations</h2>
        <p className="text-ink-muted text-sm mt-1">
          Curated from Coursera, Udemy, Google, HubSpot & more — matched to your skill gaps
        </p>
      </div>

      {courses.length === 0 ? (
        <div className="card p-8 text-center text-ink-muted">No course recommendations available.</div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {courses.map((c, i) => {
            const plt = platformBadgeStyle(c.platform)
            const stars = Math.round(c.rating)
            return (
              <div key={i} className="card p-5 flex items-start gap-4 hover:shadow-card-md transition-shadow">
                {/* Platform badge */}
                <div
                  className="w-16 flex-shrink-0 text-center py-1.5 px-1 rounded-lg text-[10px] font-bold leading-tight"
                  style={{ background: plt.bg, color: plt.text }}
                >
                  {c.platform.split('(')[0].trim()}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2 flex-wrap mb-1">
                    <h3 className="font-semibold text-sm text-ink-primary leading-snug">{c.course_name}</h3>
                    {c.skill && (
                      <span className="skill-chip chip-adv text-[10px] px-2 py-0.5 flex-shrink-0">{c.skill}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-ink-muted flex-wrap mt-1">
                    <span className="flex items-center gap-1">
                      {Array.from({ length: 5 }, (_, j) => (
                        <Star
                          key={j}
                          size={10}
                          className={j < stars ? 'fill-yellow-400 text-yellow-400' : 'text-surface-border'}
                        />
                      ))}
                      <span className="ml-0.5 font-medium text-ink-secondary">{c.rating}</span>
                    </span>
                    <span className="text-ink-muted">·</span>
                    <span>{c.duration}</span>
                    <span className="text-ink-muted">·</span>
                    <span className={`badge ${LEVEL_CLASS[c.level] || 'badge-blue'} text-[10px]`}>{c.level}</span>
                  </div>
                </div>

                {/* CTA */}
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary text-xs flex-shrink-0 flex items-center gap-1.5 px-3 py-2"
                  onClick={e => e.stopPropagation()}
                >
                  View <ExternalLink size={11} />
                </a>
              </div>
            )
          })}
        </div>
      )}

      {/* Note */}
      <div className="card p-4 bg-surface-hover text-xs text-ink-muted">
        Courses are matched to your detected skill gaps. Beginner courses are prioritised for fresher / junior profiles; advanced courses for mid / senior profiles.
      </div>
    </div>
  )
}
