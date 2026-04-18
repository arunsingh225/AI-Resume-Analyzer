import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Scan } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { authAPI } from '../services/auth'

const INPUT_CLS = `
  w-full px-4 py-3 rounded-xl text-sm text-ink-primary placeholder-stone-400
  border border-stone-200 bg-white/70 backdrop-blur-sm
  focus:outline-none focus:ring-2 focus:ring-stone-400/40 focus:border-stone-400
  transition-all duration-200
`

export default function SignupPage() {
  const { saveAuth } = useAuth()
  const navigate     = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const handleChange = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setLoading(true)
    try {
      const r = await authAPI.signup(form)
      saveAuth(r.data.token, r.data.user)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Signup failed')
    } finally { setLoading(false) }
  }

  const handleGoogle = async () => {
    setLoading(true)
    try {
      const r = await authAPI.googleLogin({
        name:       'Google User',
        email:      `google_${Date.now()}@gmail.com`,
        avatar_url: '',
      })
      saveAuth(r.data.token, r.data.user)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Google signup failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #ECEAE8 0%, #F0EEEC 50%, #E8E6E3 100%)' }}>

      <div className="absolute w-[500px] h-[400px] rounded-full -top-24 -right-24 opacity-50"
        style={{ background: 'radial-gradient(ellipse, rgba(185,195,215,0.55) 0%, transparent 70%)', filter: 'blur(40px)' }} />
      <div className="absolute w-[400px] h-[350px] rounded-full -bottom-20 -left-20 opacity-40"
        style={{ background: 'radial-gradient(ellipse, rgba(190,205,185,0.50) 0%, transparent 70%)', filter: 'blur(40px)' }} />

      <div className="relative w-full max-w-md"
        style={{
          background: 'rgba(255,255,255,0.75)', backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
          border: '1px solid rgba(255,255,255,0.60)',
          boxShadow: '0 20px 60px rgba(0,0,0,0.10), inset 0 1px 0 rgba(255,255,255,0.90)',
          borderRadius: '24px', padding: '2.5rem',
        }}>

        <div className="flex items-center gap-2.5 mb-7">
          <div className="w-9 h-9 rounded-xl bg-ink-primary flex items-center justify-center">
            <Scan size={17} className="text-white" />
          </div>
          <span className="font-display font-700 text-lg text-ink-primary tracking-tight">ResumeAI</span>
        </div>

        <h1 className="font-display text-2xl font-700 text-ink-primary mb-1">Create account</h1>
        <p className="text-sm text-ink-muted mb-7">Start analyzing your resume for free</p>

        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-warm-rose-bg border border-warm-rose-border text-warm-rose text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-ink-muted block mb-1.5">Full Name</label>
            <input name="name" required value={form.name} onChange={handleChange}
              placeholder="Your full name" className={INPUT_CLS} />
          </div>
          <div>
            <label className="text-xs font-semibold text-ink-muted block mb-1.5">Email</label>
            <input type="email" name="email" required value={form.email} onChange={handleChange}
              placeholder="you@example.com" className={INPUT_CLS} />
          </div>
          <div>
            <label className="text-xs font-semibold text-ink-muted block mb-1.5">Password</label>
            <div className="relative">
              <input type={showPwd ? 'text' : 'password'} name="password" required
                value={form.password} onChange={handleChange}
                placeholder="Minimum 6 characters" className={INPUT_CLS + ' pr-11'} />
              <button type="button" onClick={() => setShowPwd(p => !p)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600">
                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-ink-primary hover:bg-ink-secondary active:scale-[0.98] transition-all disabled:opacity-60 flex items-center justify-center gap-2 mt-2">
            {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 h-px bg-stone-200" />
          <span className="text-xs text-ink-faint">or</span>
          <div className="flex-1 h-px bg-stone-200" />
        </div>

        <button onClick={handleGoogle} disabled={loading}
          className="w-full py-3 rounded-xl border border-stone-200 bg-white/80 text-sm font-semibold text-ink-secondary hover:bg-stone-50 active:scale-[0.98] transition-all flex items-center justify-center gap-2.5 disabled:opacity-60">
          <svg width="17" height="17" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google <span className="text-[10px] text-ink-faint">(demo)</span>
        </button>

        <p className="text-center text-xs text-ink-muted mt-6">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-ink-secondary hover:text-ink-primary transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
