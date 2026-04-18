import React, { useState } from 'react'
import { useResume } from '../App'
import { matchJD } from '../services/api'
import { Target, CheckCircle2, XCircle, Lightbulb, TrendingUp, Cpu } from 'lucide-react'
import { scoreColor, scoreBgColor } from '../utils/helpers'

function ScoreRing({ pct }) {
  const C   = 2 * Math.PI * 40
  const clr = scoreColor(pct)
  return (
    <svg width="104" height="104" viewBox="0 0 104 104">
      <circle cx="52" cy="52" r="40" fill="none" stroke="#E7E5E4" strokeWidth="9" />
      <circle cx="52" cy="52" r="40" fill="none" stroke={clr} strokeWidth="9"
        strokeLinecap="round" strokeDasharray={C}
        strokeDashoffset={C - (pct / 100) * C}
        style={{ transform: 'rotate(-90deg)', transformOrigin: 'center', transition: 'stroke-dashoffset 1s ease' }}
      />
      <text x="52" y="48" textAnchor="middle" dominantBaseline="middle"
        fontSize="22" fontWeight="700" fill="#1A1917" fontFamily="Syne,sans-serif">{pct}%</text>
      <text x="52" y="66" textAnchor="middle" dominantBaseline="middle"
        fontSize="9" fill="#78716C" fontFamily="DM Sans,sans-serif">match</text>
    </svg>
  )
}

export default function JDMatchPanel() {
  const { result } = useResume()
  const [jd,      setJd]      = useState('')
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const handleMatch = async () => {
    if (!result?.raw_text_preview) { setError('Please analyze a resume first.'); return }
    if (jd.trim().length < 30)     { setError('Paste a complete job description.'); return }
    setError(''); setLoading(true)
    try {
      const res = await matchJD(result.raw_text_preview + ' ' + (result.skill_analysis?.found?.join(' ') || ''), jd)
      setData(res)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Matching failed')
    } finally { setLoading(false) }
  }

  const clr = scoreColor
  const bg  = scoreBgColor

  return (
    <div className="space-y-5 max-w-5xl">
      <div>
        <h2 className="font-display text-2xl font-700 text-ink-primary">JD Match Analyzer</h2>
        <p className="text-ink-muted text-sm mt-1">Paste a job description to see how well your resume matches it</p>
      </div>

      {/* Input */}
      <div className="card p-5">
        <label className="text-xs font-semibold text-ink-muted uppercase tracking-wide block mb-2">
          Paste Job Description
        </label>
        <textarea
          value={jd} onChange={e => setJd(e.target.value)} rows={8}
          placeholder="Paste the full job description here — including requirements, responsibilities, and qualifications…"
          className="w-full px-4 py-3 rounded-xl text-sm text-ink-primary placeholder-stone-400 border border-stone-200 bg-stone-50 focus:outline-none focus:ring-2 focus:ring-stone-300 focus:border-stone-400 resize-none transition-all font-mono leading-relaxed"
        />
        {error && <p className="text-warm-rose text-xs mt-2">{error}</p>}
        <div className="flex justify-between items-center mt-3">
          <span className="text-xs text-ink-faint">{jd.length} characters</span>
          <button onClick={handleMatch} disabled={loading}
            className="btn-primary px-6 py-2.5 text-sm disabled:opacity-60 flex items-center gap-2">
            {loading
              ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Analyzing…</>
              : <><Target size={14} />Analyze Match</>}
          </button>
        </div>
      </div>

      {/* Results */}
      {data && (
        <div className="space-y-4 animate-slide-up">

          {/* Score overview — glass */}
          <div className="glass p-6 flex flex-col sm:flex-row items-center gap-6">
            <ScoreRing pct={data.match_percent} />
            <div className="flex-1 text-center sm:text-left">
              <p className="font-display text-xl font-700 text-ink-primary mb-1">{data.verdict}</p>
              <p className="text-sm text-ink-secondary mb-4">{result?.detected_subfield} profile vs this job description</p>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: 'TF-IDF Similarity', value: `${data.tfidf_score}%`, clrFn: clr, bgFn: bg },
                  { label: 'Keyword Overlap',   value: `${data.keyword_overlap_pct}%`, clrFn: clr, bgFn: bg },
                  { label: 'Skill Overlap',     value: `${data.skill_overlap_pct}%`, clrFn: clr, bgFn: bg },
                ].map(({ label, value, clrFn, bgFn }) => (
                  <div key={label} className="text-center rounded-xl p-3"
                    style={{ background: bgFn(parseFloat(value)) }}>
                    <div className="text-lg font-display font-700" style={{ color: clrFn(parseFloat(value)) }}>{value}</div>
                    <div className="text-[10px] text-ink-muted">{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Keywords grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Matched skills */}
            <div className="card p-5">
              <h3 className="font-display font-600 text-ink-primary text-sm mb-3 flex items-center gap-2">
                <CheckCircle2 size={15} className="text-sage-600" /> Skills Matched ({data.skills_matched.length})
              </h3>
              {data.skills_matched.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {data.skills_matched.map((s, i) => <span key={i} className="skill-chip chip-found text-[11px]">{s}</span>)}
                </div>
              ) : <p className="text-xs text-ink-muted">No direct skill matches found.</p>}
            </div>

            {/* Missing skills */}
            <div className="card p-5">
              <h3 className="font-display font-600 text-ink-primary text-sm mb-3 flex items-center gap-2">
                <XCircle size={15} className="text-warm-rose" /> Skills Missing ({data.skills_missing.length})
              </h3>
              {data.skills_missing.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {data.skills_missing.map((s, i) => <span key={i} className="skill-chip chip-missing text-[11px]">{s}</span>)}
                </div>
              ) : <p className="text-xs text-ink-muted">All JD skills found in resume!</p>}
            </div>
          </div>

          {/* Keywords found vs missing */}
          <div className="card p-5">
            <h3 className="font-display font-600 text-ink-primary text-sm mb-3">Keyword Analysis</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-[10px] font-semibold text-sage-600 uppercase tracking-wide mb-2">Found in Resume ({data.keywords_found.length})</p>
                <div className="flex flex-wrap gap-1 max-h-28 overflow-hidden">
                  {data.keywords_found.map((k, i) => <span key={i} className="skill-chip chip-found text-[10px] px-2 py-0.5">{k}</span>)}
                </div>
              </div>
              <div>
                <p className="text-[10px] font-semibold text-warm-rose uppercase tracking-wide mb-2">Missing from Resume ({data.keywords_missing.length})</p>
                <div className="flex flex-wrap gap-1 max-h-28 overflow-hidden">
                  {data.keywords_missing.map((k, i) => <span key={i} className="skill-chip chip-missing text-[10px] px-2 py-0.5">{k}</span>)}
                </div>
              </div>
            </div>
          </div>

          {/* Improvement suggestions */}
          <div className="card p-5">
            <h3 className="font-display font-600 text-ink-primary text-sm mb-4 flex items-center gap-2">
              <Lightbulb size={14} className="text-warm-amber" /> How to Improve This Match
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {data.suggestions.map((s, i) => (
                <div key={i} className="flex gap-3 p-3 bg-stone-50 rounded-xl border border-stone-200">
                  <span className="text-xs font-bold text-stone-400 flex-shrink-0 w-5 text-center">{i+1}</span>
                  <p className="text-xs text-ink-secondary leading-relaxed">{s}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
