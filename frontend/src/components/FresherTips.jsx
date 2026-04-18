import React from 'react'
import { Lightbulb } from 'lucide-react'
import { useResume } from '../App'

export default function FresherTips() {
  const { result: d } = useResume()
  const tips = d.fresher_tips || []

  if (!tips.length) return null

  return (
    <div className="card p-5 mt-5">
      <h3 className="font-display font-600 text-ink-primary mb-4 flex items-center gap-2">
        <Lightbulb size={18} className="text-status-amber" />
        Fresher Tips for {d.detected_subfield}
      </h3>
      <div className="space-y-3">
        {tips.map((tip, i) => (
          <div key={i} className="flex gap-3 p-3 bg-status-amber-bg border border-status-amber-ring rounded-xl">
            <span className="text-status-amber font-bold text-sm flex-shrink-0 w-5 text-center">{i + 1}</span>
            <span className="text-sm text-ink-secondary leading-relaxed">{tip}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
