import React, { useEffect, useState } from 'react'
import { Users, FileSearch, TrendingUp, BarChart3, Award, RefreshCw } from 'lucide-react'
import api from '../services/api'

const GRADE_COLOR = { A:'#4E7245', B:'#4B5570', C:'#9E6F1A', D:'#9B3A3A', F:'#6B1A1A' }

function StatCard({ icon: Icon, label, value, sub, color = '#57534E' }) {
  return (
    <div className="card card-hover stat-card-premium p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${color}15` }}>
          <Icon size={18} style={{ color }} />
        </div>
      </div>
      <p className="text-2xl font-display font-700 mb-0.5" style={{ color }}>{value}</p>
      <p className="text-xs font-semibold text-ink-faint uppercase tracking-wide">{label}</p>
      {sub && <p className="text-xs text-ink-muted mt-1">{sub}</p>}
    </div>
  )
}

export default function AdminStats() {
  const [stats, setStats]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  const load = async () => {
    setLoading(true); setError('')
    try {
      const r = await api.get('/api/admin/stats')
      setStats(r.data)
    } catch (e) {
      setError('Could not load stats. Make sure you are signed in.')
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  if (loading) return (
    <div className="space-y-5">
      <h2 className="font-display text-2xl font-700 text-ink-primary">Platform Stats</h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card p-5 h-28 shimmer-bg" />
        ))}
      </div>
    </div>
  )

  if (error) return (
    <div className="card p-6 text-center text-warm-rose">{error}</div>
  )

  const { users, analyses } = stats

  const gradeOrder = ['A','B','C','D','F']
  const gradeTotal = Object.values(analyses.grade_distribution).reduce((a, b) => a + b, 0)

  return (
    <div className="space-y-6 stagger-enter max-w-4xl">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-700 text-ink-primary">Platform Stats</h2>
          <p className="text-ink-muted text-sm mt-1">Live usage metrics for ResumeAI</p>
        </div>
        <button onClick={load} className="btn-ghost text-xs py-2 px-3 flex items-center gap-1.5">
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* User stats */}
      <div>
        <p className="text-xs font-bold text-ink-faint uppercase tracking-widest mb-3">👥 Users</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard icon={Users}      label="Total Users"   value={users.total}       sub="All time"    color="#4E7245" />
          <StatCard icon={TrendingUp} label="New Today"     value={users.today}       sub="Last 24 hrs" color="#4B5570" />
          <StatCard icon={TrendingUp} label="This Week"     value={users.this_week}   sub="Last 7 days" color="#9E6F1A" />
          <StatCard icon={Users}      label="Google Users"  value={users.by_provider?.google || 0} sub="OAuth signups" color="#EA4335" />
        </div>
      </div>

      {/* Analysis stats */}
      <div>
        <p className="text-xs font-bold text-ink-faint uppercase tracking-widest mb-3">📄 Analyses</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard icon={FileSearch} label="Total Scans"   value={analyses.total}       sub="All time"    color="#4B5570" />
          <StatCard icon={FileSearch} label="Scans Today"   value={analyses.today}       sub="Last 24 hrs" color="#4E7245" />
          <StatCard icon={BarChart3}  label="Scans / Week"  value={analyses.this_week}   sub="Last 7 days" color="#9B3A3A" />
          <StatCard icon={Award}      label="Avg ATS Score" value={`${analyses.avg_ats_score}`} sub="Platform avg" color="#9E6F1A" />
        </div>
      </div>

      {/* Two column: top fields + grade distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Top fields */}
        <div className="card card-hover p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-4">🔥 Top Resume Fields</h3>
          <div className="space-y-3">
            {analyses.top_fields.length === 0 && (
              <p className="text-sm text-ink-muted">No data yet</p>
            )}
            {analyses.top_fields.map(({ field, count }, i) => {
              const maxCount = analyses.top_fields[0]?.count || 1
              return (
                <div key={field}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-ink-secondary font-medium capitalize">{field?.replace(/_/g,' ') || '—'}</span>
                    <span className="text-ink-muted font-semibold">{count} scans</span>
                  </div>
                  <div className="progress-bar h-2">
                    <div className="progress-fill h-full progress-fill-animated"
                      style={{ width: `${(count/maxCount)*100}%`, background: i === 0 ? '#4E7245' : '#57534E' }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Grade distribution */}
        <div className="card card-hover p-5">
          <h3 className="font-display font-600 text-ink-primary text-sm mb-4">📊 ATS Grade Distribution</h3>
          {gradeTotal === 0 ? (
            <p className="text-sm text-ink-muted">No data yet</p>
          ) : (
            <div className="space-y-3">
              {gradeOrder.map(grade => {
                const count = analyses.grade_distribution[grade] || 0
                const pct   = gradeTotal > 0 ? Math.round((count/gradeTotal)*100) : 0
                return (
                  <div key={grade} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center font-display font-700 text-sm flex-shrink-0"
                      style={{ background: `${GRADE_COLOR[grade]}15`, color: GRADE_COLOR[grade] }}>
                      {grade}
                    </div>
                    <div className="flex-1">
                      <div className="progress-bar h-2">
                        <div className="progress-fill h-full progress-fill-animated"
                          style={{ width: `${pct}%`, background: GRADE_COLOR[grade] }} />
                      </div>
                    </div>
                    <span className="text-xs text-ink-muted w-12 text-right">{count} ({pct}%)</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Provider breakdown */}
      <div className="card p-5">
        <h3 className="font-display font-600 text-ink-primary text-sm mb-4">🔐 Signup Methods</h3>
        <div className="flex gap-4 flex-wrap">
          {Object.entries(users.by_provider).map(([provider, count]) => (
            <div key={provider} className="flex items-center gap-2 bg-stone-50 border border-stone-200 px-4 py-2.5 rounded-xl">
              <span className="text-lg">
                {provider === 'google' ? '🔵' : provider === 'phone' ? '📱' : '📧'}
              </span>
              <div>
                <p className="text-sm font-bold text-ink-primary">{count}</p>
                <p className="text-[10px] text-ink-muted capitalize">{provider}</p>
              </div>
            </div>
          ))}
          {Object.keys(users.by_provider).length === 0 && (
            <p className="text-sm text-ink-muted">No signup data yet</p>
          )}
        </div>
      </div>

    </div>
  )
}
