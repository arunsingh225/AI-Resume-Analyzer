import React, { useState } from 'react'
import { useNavigate, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Target, Layers, Sparkles, FileSearch,
  Briefcase, Building2, Map, BookOpen, TrendingUp, Wand2,
  Download, Upload, Menu, X, Scan, ChevronRight, LogOut, User, Clock,
  BarChart3, PenLine
} from 'lucide-react'
import { useResume } from '../App'
import { useAuth } from '../hooks/useAuth'
import { levelLabel, levelBadgeClass } from '../utils/helpers'

import Overview            from '../components/Overview'
import ATSScoreCard        from '../components/ATSScoreCard'
import SectionAnalysis     from '../components/SectionAnalysis'
import SkillsPanel         from '../components/SkillsPanel'
import KeywordHighlighter  from '../components/KeywordHighlighter'
import JobMatchCard        from '../components/JobMatchCard'
import CompanyRecs         from '../components/CompanyRecommendations'
import RoadmapTimeline     from '../components/RoadmapTimeline'
import CourseCard          from '../components/CourseCard'
import StrengthsWeaknesses from '../components/StrengthsWeaknesses'
import ReportDownloader    from '../components/ReportDownloader'
import JDMatchPanel        from '../components/JDMatchPanel'
import ResumeImprover      from '../components/ResumeImprover'
import ResumeBuilder       from '../components/ResumeBuilder'
import AdminStats          from '../components/AdminStats'
import FeedbackWidget      from '../components/ui/FeedbackWidget'
import ThemeToggle         from '../components/ui/ThemeToggle'
import HistoryPage         from './HistoryPage'

const NAV = [
  { id: 'overview',   label: 'Overview',       Icon: LayoutDashboard, path: '' },
  { id: 'ats',        label: 'ATS Score',       Icon: Target,          path: 'ats' },
  { id: 'sections',   label: 'Sections',        Icon: Layers,          path: 'sections' },
  { id: 'skills',     label: 'Skills',          Icon: Sparkles,        path: 'skills' },
  { id: 'keywords',   label: 'Keywords',        Icon: FileSearch,      path: 'keywords' },
  { id: 'jobs',       label: 'Job Matches',     Icon: Briefcase,       path: 'jobs' },
  { id: 'companies',  label: 'Companies',       Icon: Building2,       path: 'companies' },
  { id: 'roadmap',    label: 'Roadmap',         Icon: Map,             path: 'roadmap' },
  { id: 'courses',    label: 'Courses',         Icon: BookOpen,        path: 'courses' },
  { id: 'strengths',  label: 'Strengths',       Icon: TrendingUp,      path: 'strengths' },
  null, // divider
  { id: 'jd',         label: 'JD Match',        Icon: Target,          path: 'jd', badge: 'AI' },
  { id: 'improve',    label: 'Improve Resume',  Icon: Wand2,       path: 'improve' },
  { id: 'builder',    label: 'Resume Builder',  Icon: PenLine,     path: 'builder', badge: 'NEW' },
  { id: 'history',    label: 'History',         Icon: Clock,       path: 'history' },
  null, // divider
  { id: 'report',     label: 'Download Report', Icon: Download,    path: 'report' },
  { id: 'admin',      label: 'Platform Stats',  Icon: BarChart3,   path: 'admin' },
]

function ScorePill({ score }) {
  const color = score >= 75 ? '#4E7245' : score >= 55 ? '#9E6F1A' : '#9B3A3A'
  const bg    = score >= 75 ? '#F3F6F1' : score >= 55 ? '#FAF0D7' : '#FDF4F4'
  return (
    <span className="px-3 py-1 rounded-lg text-sm font-bold font-display" style={{ color, background: bg }}>
      ATS {score}
    </span>
  )
}

function UserAvatar({ user }) {
  if (user?.avatar_url) return (
    <img src={user.avatar_url} className="w-7 h-7 rounded-full object-cover" alt={user.name} />
  )
  const initials = (user?.name || user?.email || 'U').slice(0, 2).toUpperCase()
  return (
    <div className="w-7 h-7 rounded-full bg-stone-200 flex items-center justify-center text-[11px] font-bold text-stone-600">
      {initials}
    </div>
  )
}

export default function DashboardPage() {
  const { result, setResult } = useResume()
  const { user, logout }      = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const [open, setOpen]         = useState(false)
  const [userMenu, setUserMenu] = useState(false)

  if (!result) return <Navigate to="/" />
  const d = result

  const handleNew    = () => { setResult(null); navigate('/') }
  const handleLogout = async () => { await logout(); navigate('/login') }

  const currentPath = location.pathname.replace('/dashboard', '').replace(/^\//, '')

  return (
    <div className="min-h-screen flex" style={{ background: 'linear-gradient(135deg, #ECEAE8 0%, #F0EEEC 45%, #E8E6E3 100%)' }}>

      {open && <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 lg:hidden" onClick={() => setOpen(false)} />}

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full z-40 flex flex-col w-[220px] transition-transform duration-300
        ${open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:h-auto`}
        style={{ background: 'rgba(255,255,255,0.82)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', borderRight: '1px solid rgba(255,255,255,0.55)', boxShadow: '2px 0 16px rgba(0,0,0,0.05)' }}>

        {/* Logo */}
        <div className="px-4 py-5 flex items-center justify-between border-b border-stone-200/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-ink-primary flex items-center justify-center">
              <Scan size={14} className="text-white" />
            </div>
            <span className="font-display font-700 text-base text-ink-primary tracking-tight">ResumeAI</span>
          </div>
          <button className="lg:hidden text-ink-muted" onClick={() => setOpen(false)}><X size={17} /></button>
        </div>

        {/* Candidate info */}
        <div className="px-4 py-3 border-b border-stone-200/60">
          <p className="text-sm font-semibold text-ink-primary truncate">{d.candidate_name}</p>
          <div className="flex items-center gap-1.5 mt-1 flex-wrap">
            <span className={`badge ${levelBadgeClass(d.experience_level)} text-[10px]`}>{levelLabel(d.experience_level)}</span>
            <span className="text-[10px] text-ink-muted truncate max-w-[120px]">{d.detected_subfield}</span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-3 overflow-y-auto scrollbar-thin">
          {NAV.map((item, idx) => {
            if (!item) return <div key={idx} className="my-2 border-t border-stone-200/60" />
            const { id, label, Icon, path, badge } = item
            const isActive = currentPath === path || (path === '' && currentPath === '')
            return (
              <button key={id} onClick={() => { navigate(`/dashboard/${path}`); setOpen(false) }}
                className={`nav-item relative w-full text-left text-sm mb-0.5 ${isActive ? 'active' : ''}`}>
                <Icon size={15} className="flex-shrink-0" />
                <span className="flex-1">{label}</span>
                {badge && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-stone-200 text-stone-600">{badge}</span>}
              </button>
            )
          })}
        </nav>

        {/* New analysis */}
        <div className="p-3 border-t border-stone-200/60 space-y-2">
          <button onClick={handleNew} className="btn-secondary w-full justify-center text-xs py-2">
            <Upload size={13} /> New Resume
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Topbar */}
        <header className="sticky top-0 z-20 px-4 lg:px-6 py-3.5 flex items-center gap-4 border-b"
          style={{ background: 'rgba(255,255,255,0.80)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)', borderColor: 'rgba(230,228,226,0.80)' }}>

          <button className="lg:hidden text-ink-muted p-1" onClick={() => setOpen(true)}><Menu size={20} /></button>

          {/* Breadcrumb */}
          <div className="flex-1 min-w-0 flex items-center gap-1.5 text-sm text-ink-muted overflow-hidden">
            <span className="font-semibold text-ink-secondary hidden sm:block truncate">{d.candidate_name}</span>
            <ChevronRight size={12} className="hidden sm:block flex-shrink-0" />
            <span className="truncate text-ink-muted hidden md:block">{d.detected_subfield}</span>
          </div>

          {/* Score */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <ScorePill score={d.ats_score.total} />
            <span className={`badge text-[11px] ${d.ats_score.grade === 'A' ? 'badge-sage' : d.ats_score.grade === 'B' ? 'badge-slate' : d.ats_score.grade === 'C' ? 'badge-amber' : 'badge-rose'}`}>
              {d.ats_score.grade}
            </span>
          </div>

          {/* Theme toggle + User menu */}
          <ThemeToggle />
          <div className="relative">
            <button onClick={() => setUserMenu(m => !m)}
              className="flex items-center gap-2 px-2 py-1.5 rounded-xl hover:bg-stone-100 transition-colors">
              <UserAvatar user={user} />
              <span className="text-xs font-medium text-ink-secondary hidden sm:block max-w-[80px] truncate">
                {user?.name || user?.email?.split('@')[0] || 'User'}
              </span>
            </button>

            {userMenu && (
              <div className="absolute right-0 top-full mt-2 w-52 rounded-2xl border border-stone-200 bg-white shadow-card-lg z-50 overflow-hidden dropdown-enter"
                onClick={() => setUserMenu(false)}>
                <div className="px-4 py-3 border-b border-stone-100">
                  <p className="text-sm font-semibold text-ink-primary truncate">{user?.name || 'User'}</p>
                  <p className="text-xs text-ink-muted truncate">{user?.email || user?.phone || ''}</p>
                  <span className="text-[10px] text-ink-faint">Provider: {user?.provider}</span>
                </div>
                <button onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-4 py-3 text-sm text-warm-rose hover:bg-warm-rose-bg transition-colors">
                  <LogOut size={14} /> Sign out
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-4 lg:p-6 overflow-auto scrollbar-thin">
          <div className="page-enter max-w-5xl">
            <Routes>
              <Route index           element={<Overview />} />
              <Route path="ats"      element={<ATSScoreCard />} />
              <Route path="sections" element={<SectionAnalysis />} />
              <Route path="skills"   element={<SkillsPanel />} />
              <Route path="keywords" element={<KeywordHighlighter />} />
              <Route path="jobs"     element={<JobMatchCard />} />
              <Route path="companies"element={<CompanyRecs />} />
              <Route path="roadmap"  element={<RoadmapTimeline />} />
              <Route path="courses"  element={<CourseCard />} />
              <Route path="strengths"element={<StrengthsWeaknesses />} />
              <Route path="jd"       element={<JDMatchPanel />} />
              <Route path="improve"  element={<ResumeImprover />} />
              <Route path="builder"  element={<ResumeBuilder />} />
              <Route path="history"  element={<HistoryPage />} />
              <Route path="report"   element={<ReportDownloader />} />
              <Route path="admin"    element={<AdminStats />} />
            </Routes>
          </div>
        </main>
      </div>

      {/* Click outside to close user menu */}
      {userMenu && <div className="fixed inset-0 z-40" onClick={() => setUserMenu(false)} />}

      {/* Floating feedback widget */}
      <FeedbackWidget analysisId={d?.analysis_id} page="dashboard" />
    </div>
  )
}
