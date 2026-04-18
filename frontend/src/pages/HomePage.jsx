import React, { useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Upload, CheckCircle2, AlertCircle, Scan, Cpu, BarChart3, BookOpen } from 'lucide-react'
import { useResume } from '../App'
import { analyzeResume } from '../services/api'

/* ── Scan step copy ─────────────────────────────────────────── */
const STEPS = [
  { icon: '📄', label: 'Reading document…',        sub: 'Extracting text from your resume' },
  { icon: '🔍', label: 'Detecting field…',          sub: 'Identifying your professional domain' },
  { icon: '⚡', label: 'Computing ATS score…',      sub: 'Running field-specific weighted formula' },
  { icon: '🎯', label: 'Analyzing skill gaps…',     sub: 'Comparing against 40+ field datasets' },
  { icon: '💼', label: 'Matching job roles…',       sub: 'Finding best-fit positions' },
  { icon: '🗺️', label: 'Building your roadmap…',   sub: 'Generating personalized learning plan' },
  { icon: '📊', label: 'Finalizing report…',        sub: 'Preparing full analysis dashboard' },
]

const FIELDS = [
  'Software Engineer','Frontend Developer','Backend Developer','Full Stack Developer',
  'Data Scientist','ML/AI Engineer','DevOps Engineer','Cloud Engineer',
  'Product Manager','QA Engineer','Cybersecurity Analyst','Mobile Developer',
  'Investment Banker','Financial Analyst','CA/Accountant','Risk Analyst',
  'UI/UX Designer','Graphic Designer','Motion Designer',
  'Digital Marketer','SEO Specialist','Content Writer','Social Media Manager',
  'HR Recruiter','Talent Acquisition','HRBP','L&D Specialist',
  'Corporate Lawyer','IP Lawyer','Legal Compliance',
  'Sales Executive','Business Development','Operations Executive',
  'Clinical Researcher','Healthcare Analyst','Management Consultant',
]

/* ── Fake document lines ── */
const DocLines = ({ active }) => (
  <div className="space-y-2.5 px-5 py-4 flex-1">
    {[80,95,70,60,90,50,75,85,65,80,55,70].map((w, i) => (
      <div
        key={i}
        className={`h-2 rounded-full transition-colors duration-500 ${
          active ? 'shimmer-bg' : 'bg-stone-150'
        }`}
        style={{ width: `${w}%`, animationDelay: `${i * 0.1}s` }}
      />
    ))}
  </div>
)

export default function HomePage() {
  const { setResult, setFile } = useResume()
  const navigate = useNavigate()
  const inputRef  = useRef(null)

  const [dragging,  setDragging]  = useState(false)
  const [scanning,  setScanning]  = useState(false)
  const [stepIdx,   setStepIdx]   = useState(0)
  const [progress,  setProgress]  = useState(0)
  const [error,     setError]     = useState('')
  const [fileName,  setFileName]  = useState('')
  const [fileSize,  setFileSize]  = useState('')

  /* rotate through steps while scanning */
  useEffect(() => {
    if (!scanning) return
    const iv = setInterval(() => setStepIdx(s => (s + 1) % STEPS.length), 1100)
    return () => clearInterval(iv)
  }, [scanning])

  const handleFile = useCallback(async (f) => {
    if (!f) return
    const ok = f.name.endsWith('.pdf') || f.name.endsWith('.docx') || f.name.endsWith('.doc')
    if (!ok) { setError('Only PDF and DOCX files are accepted.'); return }
    if (f.size > 10 * 1024 * 1024) { setError('File must be under 10 MB.'); return }

    setError('')
    setFile(f)
    setFileName(f.name)
    setFileSize((f.size / 1024).toFixed(0) + ' KB')
    setScanning(true)
    setStepIdx(0)
    setProgress(0)

    try {
      const data = await analyzeResume(f, p => setProgress(p))
      setResult(data)
      navigate('/dashboard')
    } catch (e) {
      setScanning(false)
      setError(
        e?.response?.data?.detail ||
        'Analysis failed. Make sure the backend is running on localhost:8000.'
      )
    }
  }, [setResult, setFile, navigate])

  const onDrop = (e) => {
    e.preventDefault(); setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const step = STEPS[stepIdx]

  return (
    <div className="relative min-h-screen flex flex-col overflow-hidden" style={{ background: 'linear-gradient(135deg, #ECEAE8 0%, #F0EEEC 45%, #E8E6E3 100%)' }}>
      {/* ── Decorative blobs ── */}
      <div className="blob w-[600px] h-[500px] bg-[#C8D4C2]/40 -top-32 -left-32" style={{ animationDuration: '20s' }} />
      <div className="blob w-[500px] h-[450px] bg-[#C2CADA]/35 -bottom-24 -right-24" style={{ animationDuration: '24s', animationDelay: '-8s' }} />
      <div className="blob w-[350px] h-[300px] bg-[#D4CCBF]/30 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style={{ animationDuration: '16s', animationDelay: '-4s' }} />

      {/* ── Navbar ── */}
      <nav className="relative z-10 px-6 py-4 flex items-center justify-between glass-subtle mx-4 mt-4 rounded-2xl">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-ink-primary flex items-center justify-center">
            <Scan size={15} className="text-ink-inverse" />
          </div>
          <span className="font-display font-700 text-base text-ink-primary tracking-tight">ResumeAI</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="badge badge-sage text-[10px] tracking-wide">v2.0</span>
          <span className="text-ink-muted text-sm hidden sm:block">40+ Field Domains</span>
        </div>
      </nav>

      {/* ── Main ── */}
      <main className="relative z-10 flex-1 flex flex-col lg:flex-row items-center justify-center gap-12 px-6 py-12 max-w-6xl mx-auto w-full">

        {/* Left — copy */}
        <div className="flex-1 max-w-lg text-center lg:text-left animate-slide-up">
          <div className="inline-flex items-center gap-2 bg-stone-100/80 text-stone-600 text-xs font-semibold px-3 py-1.5 rounded-full border border-stone-200 mb-6">
            <Cpu size={11} />
            AI-powered · MNC-grade ATS · Exact field detection
          </div>
          <h1 className="font-display text-5xl lg:text-6xl font-800 text-ink-primary mb-5 leading-[1.05] text-balance">
            Know exactly<br />
            <span className="text-stone-500">where you stand.</span>
          </h1>
          <p className="text-ink-secondary text-lg leading-relaxed mb-8 text-balance">
            Upload your resume and get a field-specific ATS score, skill gap analysis,
            job matching, and a 12-week improvement roadmap in seconds.
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-2 justify-center lg:justify-start mb-6">
            {[
              { icon: BarChart3, label: 'ATS Scoring' },
              { icon: BookOpen,  label: 'Skill Gaps' },
              { icon: FileText,  label: 'PDF & DOCX' },
              { icon: CheckCircle2, label: '40+ Fields' },
            ].map(({ icon: Icon, label }) => (
              <span key={label} className="flex items-center gap-1.5 text-xs font-medium text-ink-muted bg-surface-card/70 border border-surface-border px-3 py-1.5 rounded-lg">
                <Icon size={12} className="text-stone-400" />{label}
              </span>
            ))}
          </div>

          {/* Scrolling field pills */}
          <div>
            <p className="text-[10px] font-semibold text-ink-faint uppercase tracking-widest mb-2 text-center lg:text-left">Detected fields include</p>
            <div className="flex flex-wrap gap-1.5 justify-center lg:justify-start max-h-24 overflow-hidden">
              {FIELDS.map(f => (
                <span key={f} className="skill-chip chip-neutral text-[10px] px-2 py-0.5">{f}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Right — scanner card */}
        <div className="w-full max-w-md animate-slide-up" style={{ animationDelay: '0.1s' }}>
          {!scanning ? (
            /* Upload zone — glass card */
            <div
              onClick={() => inputRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className={`glass cursor-pointer transition-all duration-300 select-none
                ${dragging ? 'upload-zone-active scale-[1.01]' : 'hover:shadow-glass-md'}`}
              style={{ padding: '0', overflow: 'hidden' }}
            >
              {/* Top strip */}
              <div className="h-1.5 rounded-t-3xl bg-gradient-to-r from-stone-300 via-stone-400 to-stone-300" />

              {/* Document preview */}
              <div className="px-8 pt-6 pb-4">
                <div className="relative bg-white rounded-2xl shadow-card-md overflow-hidden"
                  style={{ height: '200px', border: '1px solid #E7E5E4' }}>
                  {/* Doc header */}
                  <div className="px-5 py-3.5 border-b border-stone-100 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-stone-200" />
                    <div className="w-3 h-3 rounded-full bg-stone-200" />
                    <div className="w-3 h-3 rounded-full bg-stone-200" />
                    <div className="flex-1 h-2 bg-stone-100 rounded ml-2" />
                  </div>
                  <DocLines active={false} />
                  {/* Drop hint overlay */}
                  {dragging && (
                    <div className="absolute inset-0 bg-sage-50/80 backdrop-blur-sm flex items-center justify-center rounded-2xl">
                      <div className="text-center">
                        <Upload size={28} className="text-sage-600 mx-auto mb-2" />
                        <p className="text-sage-700 font-semibold text-sm">Release to upload</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Upload CTA */}
              <div className="px-8 pb-8 text-center">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <Upload size={20} className="text-stone-400" />
                  <span className="font-display font-600 text-ink-primary text-lg">
                    {dragging ? 'Drop your resume' : 'Upload your resume'}
                  </span>
                </div>
                <p className="text-sm text-ink-muted mb-5">PDF or DOCX · Up to 10 MB</p>
                <button className="btn-primary w-full justify-center py-3 rounded-xl text-sm">
                  <Upload size={15} /> Choose File
                </button>
                <div className="flex items-center justify-center gap-4 mt-4 text-[11px] text-ink-faint">
                  <span className="flex items-center gap-1"><CheckCircle2 size={11} className="text-sage-400" /> PDF</span>
                  <span className="flex items-center gap-1"><CheckCircle2 size={11} className="text-sage-400" /> DOCX</span>
                  <span className="flex items-center gap-1"><CheckCircle2 size={11} className="text-sage-400" /> Instant results</span>
                </div>
              </div>

              <input
                ref={inputRef} type="file" accept=".pdf,.docx,.doc" className="hidden"
                onChange={e => handleFile(e.target.files[0])}
              />
            </div>

          ) : (
            /* Scanning state — glass card */
            <div className="glass-heavy" style={{ overflow: 'hidden' }}>
              {/* Top strip — animated */}
              <div className="h-1.5 rounded-t-3xl bg-gradient-to-r from-sage-200 via-sage-400 to-sage-200"
                style={{ backgroundSize: '200% 100%', animation: 'shimmer 1.8s linear infinite' }} />

              <div className="p-8">
                {/* File info */}
                <div className="flex items-center gap-3 mb-6 p-3 bg-stone-50 rounded-xl border border-stone-200">
                  <div className="w-9 h-9 rounded-lg bg-stone-100 flex items-center justify-center flex-shrink-0">
                    <FileText size={18} className="text-stone-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-ink-primary truncate">{fileName}</p>
                    <p className="text-xs text-ink-muted">{fileSize}</p>
                  </div>
                  <div className="w-2 h-2 rounded-full bg-sage-400 animate-pulse" />
                </div>

                {/* Document being scanned */}
                <div className="relative bg-white rounded-2xl overflow-hidden mb-6"
                  style={{ height: '180px', border: '1px solid #E7E5E4', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
                  <div className="px-5 py-3 border-b border-stone-100 flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-stone-200" />
                    <div className="w-24 h-2 bg-stone-100 rounded" />
                  </div>
                  <DocLines active={true} />
                  {/* Scan beam */}
                  <div className="scan-line" />
                  <div className="scan-dot" />
                </div>

                {/* Current step */}
                <div className="text-center mb-5">
                  <div className="text-2xl mb-1">{step.icon}</div>
                  <p className="font-display font-600 text-ink-primary text-base">{step.label}</p>
                  <p className="text-xs text-ink-muted mt-1">{step.sub}</p>
                </div>

                {/* Step dots */}
                <div className="flex justify-center gap-1.5 mb-5">
                  {STEPS.map((_, i) => (
                    <div
                      key={i}
                      className={`rounded-full transition-all duration-400 ${
                        i === stepIdx
                          ? 'w-5 h-2 bg-stone-500'
                          : i < stepIdx
                          ? 'w-2 h-2 bg-sage-400'
                          : 'w-2 h-2 bg-stone-200'
                      }`}
                    />
                  ))}
                </div>

                {/* Progress bar */}
                {progress > 0 && (
                  <div>
                    <div className="progress-bar h-1.5 mb-1">
                      <div className="progress-fill" style={{ width: `${progress}%`, background: '#57534E' }} />
                    </div>
                    <p className="text-[11px] text-ink-faint text-center">{progress}% uploaded</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-3 flex gap-2 p-4 bg-warm-rose-bg border border-warm-rose-border rounded-xl text-warm-rose text-sm">
              <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </main>

      <footer className="relative z-10 text-center py-4 text-[11px] text-ink-faint">
        ResumeAI v2.0 · FastAPI backend · PDF & DOCX · 40+ exact field domains
      </footer>
    </div>
  )
}
