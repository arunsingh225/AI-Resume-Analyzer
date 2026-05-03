import React, { useState, useRef } from 'react'
import { FileText, Download, Sparkles, CheckCircle2, ChevronRight, Plus, Trash2, Eye } from 'lucide-react'

// ── ATS-Optimized Templates ────────────────────────────────────────────────
const TEMPLATES = [
  {
    id: 'classic',
    name: 'Classic ATS',
    desc: 'Clean single-column layout. Best ATS pass rate. Preferred by FAANG & MNCs.',
    badge: 'Highest ATS Score',
    badgeColor: '#4E7245',
    ats: 98,
    preview: '#F8F7F6',
    accent: '#1A1917',
    recommended: true,
  },
  {
    id: 'modern',
    name: 'Modern Pro',
    desc: 'Subtle left-sidebar accent with clean typography. Works well for tech roles.',
    badge: 'Tech Roles',
    badgeColor: '#4B5570',
    ats: 94,
    preview: '#F0F0F8',
    accent: '#4B5570',
    recommended: false,
  },
  {
    id: 'minimal',
    name: 'Minimal Clean',
    desc: 'Ultra-minimal with generous whitespace. Great for product, design & consulting.',
    badge: 'Premium Look',
    badgeColor: '#9E6F1A',
    ats: 92,
    preview: '#FAFAFA',
    accent: '#9E6F1A',
    recommended: false,
  },
  {
    id: 'executive',
    name: 'Executive',
    desc: 'Bold name header with ruled sections. Ideal for senior & leadership roles.',
    badge: 'Senior Roles',
    badgeColor: '#9B3A3A',
    ats: 91,
    preview: '#FBF8F8',
    accent: '#9B3A3A',
    recommended: false,
  },
]

const ATS_TIPS = [
  'Use standard section headings: Experience, Education, Skills',
  'Avoid tables, columns, headers/footers, and text boxes',
  'Use plain bullet points (•), not icons or custom symbols',
  'Save as PDF — always',
  'Include keywords from the job description naturally',
  'Use standard fonts: Arial, Calibri, Helvetica, Times New Roman',
  'Keep file size under 2MB',
  'Put contact info in the body, not in a header element',
]

const EMPTY_FORM = {
  name: '', email: '', phone: '', linkedin: '', github: '',
  summary: '',
  skills: '',
  experience: [{ company: '', role: '', duration: '', bullets: '' }],
  education: [{ institution: '', degree: '', year: '', gpa: '' }],
  projects: [{ name: '', tech: '', bullets: '' }],
  certifications: '',
  achievements: '',
}

function SectionHeader({ title, onAdd, addLabel }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h3 className="font-display font-600 text-ink-primary text-sm">{title}</h3>
      {onAdd && (
        <button onClick={onAdd} className="btn-ghost text-xs py-1 px-2 flex items-center gap-1">
          <Plus size={11} /> {addLabel || 'Add'}
        </button>
      )}
    </div>
  )
}

const INPUT = `w-full px-3 py-2.5 rounded-xl text-sm text-ink-primary placeholder-stone-400
  border border-stone-200 bg-white/70 focus:outline-none focus:ring-2
  focus:ring-stone-300/50 focus:border-stone-400 transition-all`

const TEXTAREA = INPUT + ' resize-none'

export default function ResumeBuilder() {
  const [selected, setSelected]   = useState('classic')
  const [tab, setTab]             = useState('template') // template | build | tips
  const [form, setForm]           = useState(EMPTY_FORM)
  const [preview, setPreview]     = useState(false)
  const printRef = useRef(null)

  const template = TEMPLATES.find(t => t.id === selected)

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))
  const setArr = (key, idx, field, val) =>
    setForm(f => ({ ...f, [key]: f[key].map((item, i) => i === idx ? { ...item, [field]: val } : item) }))
  const addArr = (key, empty) =>
    setForm(f => ({ ...f, [key]: [...f[key], empty] }))
  const delArr = (key, idx) =>
    setForm(f => ({ ...f, [key]: f[key].filter((_, i) => i !== idx) }))

  const handleDownload = () => {
    window.print()
  }

  return (
    <div className="space-y-5 max-w-5xl stagger-enter">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-700 text-ink-primary">Resume Builder</h2>
          <p className="text-ink-muted text-sm mt-1">Create an ATS-optimized resume from scratch</p>
        </div>
        {tab === 'build' && (
          <button onClick={handleDownload}
            className="btn-primary text-sm py-2.5 px-4 flex items-center gap-2">
            <Download size={14} /> Download PDF
          </button>
        )}
      </div>

      {/* Tab bar */}
      <div className="flex bg-stone-100 rounded-xl p-1 max-w-sm">
        {[
          { id: 'template', label: '1. Pick Template' },
          { id: 'build',    label: '2. Build Resume' },
          { id: 'tips',     label: '3. ATS Tips' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all whitespace-nowrap px-2
              ${tab === t.id ? 'bg-white shadow-card text-ink-primary' : 'text-ink-muted'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── TAB: Template Picker ── */}
      {tab === 'template' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {TEMPLATES.map(t => (
              <div key={t.id} onClick={() => setSelected(t.id)}
                className={`card card-hover p-4 cursor-pointer transition-all ${selected === t.id ? 'ring-2 ring-offset-2' : ''}`}
                style={{ ringColor: t.accent }}>
                {/* Template preview swatch */}
                <div className="h-28 rounded-xl mb-3 flex items-center justify-center relative overflow-hidden"
                  style={{ background: t.preview, border: `2px solid ${t.accent}20` }}>
                  {/* Mock resume lines */}
                  <div className="w-3/4 space-y-1.5 px-4">
                    <div className="h-2.5 rounded-full w-1/2" style={{ background: t.accent }} />
                    <div className="h-1.5 rounded-full w-3/4 bg-stone-200" />
                    <div className="h-px bg-stone-200 my-1" />
                    <div className="h-1.5 rounded-full w-full bg-stone-200" />
                    <div className="h-1.5 rounded-full w-5/6 bg-stone-200" />
                    <div className="h-1.5 rounded-full w-4/5 bg-stone-200" />
                    <div className="h-px bg-stone-200 my-1" />
                    <div className="h-1.5 rounded-full w-2/3 bg-stone-200" />
                    <div className="h-1.5 rounded-full w-3/4 bg-stone-200" />
                  </div>
                  {t.recommended && (
                    <div className="absolute top-2 right-2 text-[9px] font-bold px-2 py-0.5 rounded-full text-white"
                      style={{ background: '#4E7245' }}>BEST</div>
                  )}
                  {selected === t.id && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/10 rounded-xl">
                      <CheckCircle2 size={28} className="text-white drop-shadow" />
                    </div>
                  )}
                </div>

                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <h3 className="font-display font-600 text-ink-primary text-sm">{t.name}</h3>
                    <p className="text-xs text-ink-muted leading-relaxed mt-0.5">{t.desc}</p>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full whitespace-nowrap flex-shrink-0"
                    style={{ background: `${t.badgeColor}15`, color: t.badgeColor }}>
                    {t.badge}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-1.5">
                  <div className="flex-1 progress-bar h-1.5">
                    <div className="progress-fill h-full" style={{ width: `${t.ats}%`, background: t.badgeColor }} />
                  </div>
                  <span className="text-[10px] font-bold" style={{ color: t.badgeColor }}>ATS {t.ats}%</span>
                </div>
              </div>
            ))}
          </div>

          <button onClick={() => setTab('build')}
            className="btn-primary py-3 px-6 flex items-center gap-2">
            Use {template.name} Template <ChevronRight size={15} />
          </button>
        </div>
      )}

      {/* ── TAB: Build Resume ── */}
      {tab === 'build' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* Form */}
          <div className="space-y-4 max-h-[80vh] overflow-y-auto scrollbar-thin pr-1">

            {/* Contact */}
            <div className="card p-5">
              <SectionHeader title="📋 Contact Information" />
              <div className="space-y-3">
                <input className={INPUT} placeholder="Full Name *" value={form.name} onChange={e => set('name', e.target.value)} />
                <div className="grid grid-cols-2 gap-2">
                  <input className={INPUT} placeholder="Email *" value={form.email} onChange={e => set('email', e.target.value)} />
                  <input className={INPUT} placeholder="Phone" value={form.phone} onChange={e => set('phone', e.target.value)} />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input className={INPUT} placeholder="LinkedIn URL" value={form.linkedin} onChange={e => set('linkedin', e.target.value)} />
                  <input className={INPUT} placeholder="GitHub URL" value={form.github} onChange={e => set('github', e.target.value)} />
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="card p-5">
              <SectionHeader title="🎯 Professional Summary" />
              <textarea className={TEXTAREA} rows={3}
                placeholder="3-4 lines with your top skills, years of experience, and career goal..."
                value={form.summary} onChange={e => set('summary', e.target.value)} />
            </div>

            {/* Skills */}
            <div className="card p-5">
              <SectionHeader title="⚡ Technical Skills" />
              <textarea className={TEXTAREA} rows={3}
                placeholder="Languages: Python, Java&#10;Tools: Git, Docker, VS Code&#10;ML: Scikit-learn, TensorFlow"
                value={form.skills} onChange={e => set('skills', e.target.value)} />
            </div>

            {/* Experience */}
            <div className="card p-5">
              <SectionHeader title="💼 Work Experience"
                onAdd={() => addArr('experience', { company:'', role:'', duration:'', bullets:'' })}
                addLabel="Add Job" />
              {form.experience.map((exp, i) => (
                <div key={i} className="border border-stone-200 rounded-xl p-3 mb-3 space-y-2 relative">
                  {form.experience.length > 1 && (
                    <button onClick={() => delArr('experience', i)}
                      className="absolute top-2 right-2 text-stone-400 hover:text-warm-rose">
                      <Trash2 size={13} />
                    </button>
                  )}
                  <div className="grid grid-cols-2 gap-2">
                    <input className={INPUT} placeholder="Company Name" value={exp.company}
                      onChange={e => setArr('experience', i, 'company', e.target.value)} />
                    <input className={INPUT} placeholder="Role / Title" value={exp.role}
                      onChange={e => setArr('experience', i, 'role', e.target.value)} />
                  </div>
                  <input className={INPUT} placeholder="Duration (e.g. Jan 2024 – Present)" value={exp.duration}
                    onChange={e => setArr('experience', i, 'duration', e.target.value)} />
                  <textarea className={TEXTAREA} rows={3}
                    placeholder="• Built X that improved Y by Z%&#10;• Developed feature using React and FastAPI"
                    value={exp.bullets} onChange={e => setArr('experience', i, 'bullets', e.target.value)} />
                </div>
              ))}
            </div>

            {/* Education */}
            <div className="card p-5">
              <SectionHeader title="🎓 Education"
                onAdd={() => addArr('education', { institution:'', degree:'', year:'', gpa:'' })}
                addLabel="Add" />
              {form.education.map((edu, i) => (
                <div key={i} className="border border-stone-200 rounded-xl p-3 mb-3 space-y-2 relative">
                  {form.education.length > 1 && (
                    <button onClick={() => delArr('education', i)}
                      className="absolute top-2 right-2 text-stone-400 hover:text-warm-rose">
                      <Trash2 size={13} />
                    </button>
                  )}
                  <input className={INPUT} placeholder="Institution Name" value={edu.institution}
                    onChange={e => setArr('education', i, 'institution', e.target.value)} />
                  <div className="grid grid-cols-2 gap-2">
                    <input className={INPUT} placeholder="Degree" value={edu.degree}
                      onChange={e => setArr('education', i, 'degree', e.target.value)} />
                    <input className={INPUT} placeholder="Year / CGPA" value={edu.year}
                      onChange={e => setArr('education', i, 'year', e.target.value)} />
                  </div>
                </div>
              ))}
            </div>

            {/* Projects */}
            <div className="card p-5">
              <SectionHeader title="🚀 Projects"
                onAdd={() => addArr('projects', { name:'', tech:'', bullets:'' })}
                addLabel="Add Project" />
              {form.projects.map((proj, i) => (
                <div key={i} className="border border-stone-200 rounded-xl p-3 mb-3 space-y-2 relative">
                  {form.projects.length > 1 && (
                    <button onClick={() => delArr('projects', i)}
                      className="absolute top-2 right-2 text-stone-400 hover:text-warm-rose">
                      <Trash2 size={13} />
                    </button>
                  )}
                  <div className="grid grid-cols-2 gap-2">
                    <input className={INPUT} placeholder="Project Name" value={proj.name}
                      onChange={e => setArr('projects', i, 'name', e.target.value)} />
                    <input className={INPUT} placeholder="Stack / Tech" value={proj.tech}
                      onChange={e => setArr('projects', i, 'tech', e.target.value)} />
                  </div>
                  <textarea className={TEXTAREA} rows={2}
                    placeholder="• What it does and the impact..."
                    value={proj.bullets} onChange={e => setArr('projects', i, 'bullets', e.target.value)} />
                </div>
              ))}
            </div>

            {/* Certs & Achievements */}
            <div className="card p-5 space-y-4">
              <div>
                <SectionHeader title="📜 Certifications" />
                <textarea className={TEXTAREA} rows={2}
                  placeholder="• Oracle Cloud Infrastructure 2025 – AI Professional"
                  value={form.certifications} onChange={e => set('certifications', e.target.value)} />
              </div>
              <div>
                <SectionHeader title="🏆 Achievements" />
                <textarea className={TEXTAREA} rows={2}
                  placeholder="• EY Techathon – Qualified Round 1&#10;• LeetCode – 27 problems solved"
                  value={form.achievements} onChange={e => set('achievements', e.target.value)} />
              </div>
            </div>
          </div>

          {/* Live Preview */}
          <div className="sticky top-20">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-bold text-ink-faint uppercase tracking-widest">Live Preview</p>
              <span className="badge badge-sage text-[10px]">{template.name}</span>
            </div>
            <div ref={printRef} id="resume-preview"
              className="bg-white rounded-2xl shadow-card-lg overflow-auto"
              style={{ maxHeight: '75vh', fontSize: '11px', padding: '24px', color: '#1A1917' }}>
              <ResumePreview form={form} template={template} />
            </div>
          </div>
        </div>
      )}

      {/* ── TAB: ATS Tips ── */}
      {tab === 'tips' && (
        <div className="space-y-4 max-w-2xl">
          <div className="glass p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-sage-100 flex items-center justify-center">
                <Sparkles size={18} className="text-sage-700" />
              </div>
              <div>
                <h3 className="font-display font-600 text-ink-primary">ATS Optimization Rules</h3>
                <p className="text-xs text-ink-muted">Follow these to maximize your ATS pass rate</p>
              </div>
            </div>
            <ul className="space-y-3">
              {ATS_TIPS.map((tip, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ background: '#4E724515', color: '#4E7245' }}>
                    <span className="text-[10px] font-bold">{i+1}</span>
                  </div>
                  <span className="text-ink-secondary leading-relaxed">{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="card p-5">
            <h3 className="font-display font-600 text-ink-primary text-sm mb-3">🎯 Suggested Template for Your Field</h3>
            <div className="space-y-2">
              {[
                { field: 'Software / Data / ML / DevOps', template: 'Classic ATS or Modern Pro' },
                { field: 'Design / UI-UX', template: 'Minimal Clean (still ATS-safe)' },
                { field: 'Finance / Consulting', template: 'Executive' },
                { field: 'Freshers / Students', template: 'Classic ATS (highest pass rate)' },
                { field: 'Marketing / Content', template: 'Modern Pro' },
              ].map(({ field, template }) => (
                <div key={field} className="flex items-center justify-between py-2 border-b border-stone-100 last:border-0">
                  <span className="text-sm text-ink-secondary">{field}</span>
                  <span className="text-xs font-semibold text-ink-primary bg-stone-100 px-2 py-1 rounded-lg">{template}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Resume Preview Component ────────────────────────────────────────────────
function ResumePreview({ form, template }) {
  const acc = template.accent
  const bullets = (text) => text.split('\n').filter(Boolean)

  return (
    <div style={{ fontFamily: 'Arial, Helvetica, sans-serif', lineHeight: 1.4 }}>

      {/* Header */}
      <div style={{ borderBottom: `2px solid ${acc}`, paddingBottom: 10, marginBottom: 10 }}>
        <div style={{ fontSize: 20, fontWeight: 700, color: acc }}>{form.name || 'Your Name'}</div>
        <div style={{ fontSize: 10, color: '#57534E', marginTop: 3 }}>
          {[form.email, form.phone, form.linkedin, form.github].filter(Boolean).join(' • ')}
        </div>
      </div>

      {/* Summary */}
      {form.summary && (
        <Section title="PROFESSIONAL SUMMARY" acc={acc}>
          <p style={{ color: '#44403C' }}>{form.summary}</p>
        </Section>
      )}

      {/* Skills */}
      {form.skills && (
        <Section title="TECHNICAL SKILLS" acc={acc}>
          {form.skills.split('\n').filter(Boolean).map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </Section>
      )}

      {/* Experience */}
      {form.experience.some(e => e.company || e.role) && (
        <Section title="WORK EXPERIENCE" acc={acc}>
          {form.experience.filter(e => e.company || e.role).map((exp, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700, color: '#1A1917' }}>{exp.role || 'Role'}</span>
                <span style={{ color: '#78716C' }}>{exp.duration}</span>
              </div>
              <div style={{ color: acc, fontWeight: 600, marginBottom: 3 }}>{exp.company}</div>
              {bullets(exp.bullets).map((b, j) => (
                <div key={j} style={{ paddingLeft: 12 }}>• {b.replace(/^•\s*/, '')}</div>
              ))}
            </div>
          ))}
        </Section>
      )}

      {/* Projects */}
      {form.projects.some(p => p.name) && (
        <Section title="PROJECTS" acc={acc}>
          {form.projects.filter(p => p.name).map((proj, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <span style={{ fontWeight: 700 }}>{proj.name}</span>
              {proj.tech && <span style={{ color: '#78716C' }}> | {proj.tech}</span>}
              {bullets(proj.bullets).map((b, j) => (
                <div key={j} style={{ paddingLeft: 12 }}>• {b.replace(/^•\s*/, '')}</div>
              ))}
            </div>
          ))}
        </Section>
      )}

      {/* Education */}
      {form.education.some(e => e.institution) && (
        <Section title="EDUCATION" acc={acc}>
          {form.education.filter(e => e.institution).map((edu, i) => (
            <div key={i} style={{ marginBottom: 6 }}>
              <div style={{ fontWeight: 700 }}>{edu.degree} | {edu.institution}</div>
              <div style={{ color: '#78716C' }}>{edu.year}</div>
            </div>
          ))}
        </Section>
      )}

      {/* Certifications */}
      {form.certifications && (
        <Section title="CERTIFICATIONS" acc={acc}>
          {bullets(form.certifications).map((b, i) => (
            <div key={i}>• {b.replace(/^•\s*/, '')}</div>
          ))}
        </Section>
      )}

      {/* Achievements */}
      {form.achievements && (
        <Section title="ACHIEVEMENTS" acc={acc}>
          {bullets(form.achievements).map((b, i) => (
            <div key={i}>• {b.replace(/^•\s*/, '')}</div>
          ))}
        </Section>
      )}
    </div>
  )
}

function Section({ title, acc, children }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: acc, borderBottom: `1px solid ${acc}40`,
        paddingBottom: 2, marginBottom: 5, letterSpacing: '0.08em' }}>{title}</div>
      <div style={{ fontSize: 10, color: '#44403C' }}>{children}</div>
    </div>
  )
}
