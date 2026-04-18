import React, { useState } from 'react'
import { Download, FileJson, FileText, CheckCircle2, AlertCircle } from 'lucide-react'
import { useResume } from '../App'
import { downloadJsonReport, downloadPdfReport } from '../services/api'

export default function ReportDownloader() {
  const { result: d } = useResume()
  const [status, setStatus] = useState({ json: 'idle', pdf: 'idle' })
  const [error,  setError]  = useState('')

  const handle = async (type) => {
    setError('')
    setStatus(s => ({ ...s, [type]: 'loading' }))
    try {
      if (type === 'json') await downloadJsonReport(d)
      else                 await downloadPdfReport(d)
      setStatus(s => ({ ...s, [type]: 'done' }))
      setTimeout(() => setStatus(s => ({ ...s, [type]: 'idle' })), 3000)
    } catch (e) {
      setStatus(s => ({ ...s, [type]: 'idle' }))
      setError(
        type === 'pdf'
          ? 'PDF generation requires reportlab on the backend: pip install reportlab'
          : 'JSON download failed. Is the backend running?'
      )
    }
  }

  const ReportCard = ({ type, Icon, title, description, btnLabel, btnClass }) => {
    const st = status[type]
    return (
      <div className="card p-6 flex flex-col items-start gap-4">
        <div className="w-12 h-12 rounded-2xl bg-surface-base flex items-center justify-center">
          <Icon size={24} className="text-brand-600" />
        </div>
        <div>
          <h3 className="font-display font-700 text-ink-primary mb-1">{title}</h3>
          <p className="text-sm text-ink-secondary leading-relaxed">{description}</p>
        </div>
        <button
          onClick={() => handle(type)}
          disabled={st === 'loading'}
          className={`${btnClass} flex items-center gap-2 text-sm font-semibold px-5 py-2.5 rounded-xl transition-all disabled:opacity-60`}
        >
          {st === 'loading' && <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />}
          {st === 'done'    && <CheckCircle2 size={16} />}
          {st === 'idle'    && <Download size={16} />}
          {st === 'loading' ? 'Generating…' : st === 'done' ? 'Downloaded!' : btnLabel}
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-5 max-w-3xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">Download Reports</h2>
        <p className="text-ink-muted text-sm mt-1">Export your full analysis as JSON or PDF</p>
      </div>

      {error && (
        <div className="flex gap-2 p-4 bg-status-red-bg border border-status-red-ring rounded-xl text-status-red text-sm">
          <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ReportCard
          type="json" Icon={FileJson} title="JSON Report"
          description="Machine-readable full analysis. Useful for developers, integrations, or building your own tools on top of the data."
          btnLabel="Download JSON"
          btnClass="bg-brand-600 hover:bg-brand-700 text-white"
        />
        <ReportCard
          type="pdf" Icon={FileText} title="PDF Report"
          description="Professional formatted report with ATS score breakdown, skill gaps, job matches, and 12-week roadmap — ready to share."
          btnLabel="Download PDF"
          btnClass="bg-ink-primary hover:bg-ink-secondary text-white"
        />
      </div>

      {/* Preview */}
      <div className="card p-5">
        <h3 className="font-display font-600 text-ink-primary mb-3">Report Preview (JSON)</h3>
        <pre className="text-xs font-mono text-ink-secondary bg-surface-base rounded-xl p-4 overflow-auto max-h-72 scrollbar-thin leading-relaxed">
          {JSON.stringify({
            candidate_name:    d.candidate_name,
            detected_field:    d.detected_field,
            detected_subfield: d.detected_subfield,
            experience_level:  d.experience_level,
            years_experience:  d.years_experience,
            file_type:         d.file_type,
            ats_score:         d.ats_score,
            skills_found:      d.skill_analysis?.found?.slice(0, 8),
            skills_missing:    d.skill_analysis?.missing?.slice(0, 6),
            top_job_match:     d.job_matches?.[0],
            keywords_found:    d.keywords_found?.slice(0, 8),
            keywords_missing:  d.keywords_missing?.slice(0, 6),
          }, null, 2)}
        </pre>
      </div>
    </div>
  )
}
