import React, { useEffect, useState } from 'react'
import { FileText } from 'lucide-react'

export default function Loader({ step, fileName, progress }) {
  const [dots, setDots] = useState('.')
  useEffect(() => {
    const iv = setInterval(() => setDots(d => d.length >= 3 ? '.' : d + '.'), 500)
    return () => clearInterval(iv)
  }, [])

  return (
    <div className="min-h-screen bg-surface-base flex flex-col items-center justify-center px-4">
      {/* Document with scan line */}
      <div className="relative w-48 h-64 mb-10">
        {/* Document body */}
        <div className="absolute inset-0 bg-surface-card border border-surface-border rounded-2xl shadow-card-lg overflow-hidden">
          {/* Header strip */}
          <div className="h-1.5 bg-brand-600 rounded-t-2xl" />
          {/* Fake content lines */}
          <div className="p-5 space-y-3">
            <div className="h-3 bg-surface-border rounded w-3/4" />
            <div className="h-2.5 bg-surface-border rounded w-full" />
            <div className="h-2.5 bg-surface-border rounded w-5/6" />
            <div className="h-2.5 bg-surface-border rounded w-4/6" />
            <div className="mt-4 h-2 bg-surface-border rounded w-1/3" />
            <div className="h-2.5 bg-surface-border rounded w-full" />
            <div className="h-2.5 bg-surface-border rounded w-5/6" />
            <div className="h-2.5 bg-surface-border rounded w-3/4" />
            <div className="mt-3 h-2 bg-surface-border rounded w-1/3" />
            <div className="h-2.5 bg-surface-border rounded w-full" />
            <div className="h-2.5 bg-surface-border rounded w-2/3" />
          </div>
          {/* Scan line */}
          <div className="scan-line" />
        </div>

        {/* Pulsing ring */}
        <div className="absolute -inset-3 rounded-3xl border-2 border-brand-200 animate-pulse-ring" />
        <div className="absolute -inset-6 rounded-3xl border border-brand-100 animate-pulse-ring" style={{ animationDelay: '0.5s' }} />

        {/* File icon badge */}
        <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-brand-600 rounded-2xl shadow-card-md flex items-center justify-center">
          <FileText size={20} className="text-white" />
        </div>
      </div>

      {/* Step text */}
      <h2 className="font-display text-2xl font-700 text-ink-primary mb-2 text-center">
        Analyzing Resume{dots}
      </h2>
      {fileName && (
        <p className="text-ink-muted text-sm mb-1 font-mono truncate max-w-xs text-center">{fileName}</p>
      )}
      <p className="text-brand-600 text-sm font-medium mb-8 text-center min-h-[1.5rem]">{step}</p>

      {/* Progress bar */}
      <div className="w-64 h-1.5 bg-surface-border rounded-full overflow-hidden">
        <div
          className="h-full bg-brand-600 rounded-full transition-all duration-300"
          style={{ width: `${Math.max(progress, 5)}%` }}
        />
      </div>
      <p className="text-xs text-ink-muted mt-2">{progress > 0 ? `${progress}% uploaded` : 'Processing…'}</p>
    </div>
  )
}
