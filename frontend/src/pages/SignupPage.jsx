import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Scan } from 'lucide-react'
import { GoogleLogin } from '@react-oauth/google'
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
  const [slowHint, setSlowHint] = useState(false)

  const handleChange = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const withSlowHint = (fn) => async (...args) => {
    const timer = setTimeout(() => setSlowHint(true), 5000)
    try { return await fn(...args) }
    finally { clearTimeout(timer); setSlowHint(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setLoading(true)
    try {
      const r = await withSlowHint(() => authAPI.signup(form))()
      saveAuth(r.data)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Signup failed')
    } finally { setLoading(false) }
  }

  // Real Google OAuth — receives verified credential JWT from Google
  const handleGoogleSuccess = async (credentialResponse) => {
    setError(''); setLoading(true)
    try {
      const r = await withSlowHint(() =>
        authAPI.googleLogin({ credential: credentialResponse.credential })
      )()
      saveAuth(r.data)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Google signup failed')
    } finally { setLoading(false) }
  }

  const handleGoogleError = () => {
    setError('Google sign-in was cancelled or failed. Please try again.')
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

        {slowHint && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 text-sm flex items-center gap-2">
            <span className="w-4 h-4 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin flex-shrink-0" />
            Server is waking up (free tier). This takes ~15-30 seconds…
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

        {/* Real Google Sign-In — no more mock/demo */}
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            theme="outline"
            size="large"
            width="100%"
            text="signup_with"
            shape="pill"
          />
        </div>

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
