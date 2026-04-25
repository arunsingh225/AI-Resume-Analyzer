import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Smartphone, Mail, ArrowLeft, Scan } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { authAPI } from '../services/auth'

const INPUT_CLS = `
  w-full px-4 py-3 rounded-xl text-sm text-ink-primary placeholder-stone-400
  border border-stone-200 bg-white/70 backdrop-blur-sm
  focus:outline-none focus:ring-2 focus:ring-stone-400/40 focus:border-stone-400
  transition-all duration-200
`
const BTN_PRIMARY = `
  w-full py-3 rounded-xl text-sm font-semibold text-white
  bg-ink-primary hover:bg-ink-secondary active:scale-[0.98]
  transition-all duration-150 flex items-center justify-center gap-2
`

export default function LoginPage() {
  const { saveAuth }  = useAuth()
  const navigate      = useNavigate()
  const [tab, setTab] = useState('email')   // 'email' | 'otp'

  // email/pass
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [showPwd,  setShowPwd]  = useState(false)

  // OTP
  const [phone,    setPhone]    = useState('')
  const [otp,      setOtp]      = useState('')
  const [demoOtp,  setDemoOtp]  = useState('')
  const [otpSent,  setOtpSent]  = useState(false)

  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')

  const finish = (data) => {
    saveAuth(data)
    navigate('/', { replace: true })
  }

  const handleEmail = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const r = await authAPI.login({ email, password })
      finish(r.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally { setLoading(false) }
  }

  const handleGoogle = async () => {
    setError(''); setLoading(true)
    // Mock: pre-fill a demo Google user
    try {
      const r = await authAPI.googleLogin({
        name:       'Google User',
        email:      `google_${Date.now()}@gmail.com`,
        avatar_url: 'https://ui-avatars.com/api/?name=Google+User&background=E7E5E4&color=44403C',
      })
      finish(r.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Google login failed')
    } finally { setLoading(false) }
  }

  const handleSendOTP = async () => {
    if (phone.length < 10) { setError('Enter a valid phone number'); return }
    setError(''); setLoading(true)
    try {
      await authAPI.sendOTP(phone)
      setOtpSent(true)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send OTP')
    } finally { setLoading(false) }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const r = await authAPI.verifyOTP({ phone, otp })
      finish(r.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Invalid OTP')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #ECEAE8 0%, #F0EEEC 50%, #E8E6E3 100%)' }}>

      {/* Blobs */}
      <div className="absolute w-[500px] h-[400px] rounded-full -top-24 -left-24 opacity-50"
        style={{ background: 'radial-gradient(ellipse, rgba(190,205,185,0.55) 0%, transparent 70%)', filter: 'blur(40px)' }} />
      <div className="absolute w-[400px] h-[400px] rounded-full -bottom-20 -right-20 opacity-40"
        style={{ background: 'radial-gradient(ellipse, rgba(185,195,215,0.50) 0%, transparent 70%)', filter: 'blur(40px)' }} />

      {/* Glass Card */}
      <div className="relative w-full max-w-md"
        style={{
          background: 'rgba(255,255,255,0.75)', backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
          border: '1px solid rgba(255,255,255,0.60)',
          boxShadow: '0 20px 60px rgba(0,0,0,0.10), inset 0 1px 0 rgba(255,255,255,0.90)',
          borderRadius: '24px', padding: '2.5rem',
        }}>

        {/* Logo */}
        <div className="flex items-center gap-2.5 mb-7">
          <div className="w-9 h-9 rounded-xl bg-ink-primary flex items-center justify-center">
            <Scan size={17} className="text-white" />
          </div>
          <span className="font-display font-700 text-lg text-ink-primary tracking-tight">ResumeAI</span>
        </div>

        <h1 className="font-display text-2xl font-700 text-ink-primary mb-1">Welcome back</h1>
        <p className="text-sm text-ink-muted mb-7">Sign in to your account to continue</p>

        {/* Tab switcher */}
        <div className="flex bg-stone-100 rounded-xl p-1 mb-6">
          <button onClick={() => { setTab('email'); setError('') }}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${tab === 'email' ? 'bg-white shadow-card text-ink-primary' : 'text-ink-muted'}`}>
            <Mail size={13} className="inline mr-1.5" />Email
          </button>
          <button onClick={() => { setTab('otp'); setError('') }}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${tab === 'otp' ? 'bg-white shadow-card text-ink-primary' : 'text-ink-muted'}`}>
            <Smartphone size={13} className="inline mr-1.5" />Phone
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-warm-rose-bg border border-warm-rose-border text-warm-rose text-sm">
            {error}
          </div>
        )}

        {/* Email/Password form */}
        {tab === 'email' && (
          <form onSubmit={handleEmail} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-ink-muted block mb-1.5">Email</label>
              <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com" className={INPUT_CLS} />
            </div>
            <div>
              <label className="text-xs font-semibold text-ink-muted block mb-1.5">Password</label>
              <div className="relative">
                <input type={showPwd ? 'text' : 'password'} required value={password}
                  onChange={e => setPassword(e.target.value)} placeholder="••••••••"
                  className={INPUT_CLS + ' pr-11'} />
                <button type="button" onClick={() => setShowPwd(p => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600">
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className={BTN_PRIMARY + ' mt-2 disabled:opacity-60'}>
              {loading ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
        )}

        {/* OTP form */}
        {tab === 'otp' && (
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-ink-muted block mb-1.5">Phone Number</label>
              <div className="flex gap-2">
                <input value={phone} onChange={e => setPhone(e.target.value)}
                  placeholder="+91 9876543210" className={INPUT_CLS + ' flex-1'}
                  disabled={otpSent} />
                {!otpSent && (
                  <button onClick={handleSendOTP} disabled={loading}
                    className="px-4 py-3 rounded-xl bg-ink-primary text-white text-sm font-semibold disabled:opacity-60 whitespace-nowrap hover:bg-ink-secondary transition-colors">
                    {loading ? '…' : 'Send OTP'}
                  </button>
                )}
              </div>
            </div>

            {otpSent && (
              <form onSubmit={handleVerifyOTP} className="space-y-3">
                <div>
                  <label className="text-xs font-semibold text-ink-muted block mb-1.5">Enter OTP</label>
                  <input value={otp} onChange={e => setOtp(e.target.value)}
                    placeholder="6-digit OTP" maxLength={6} className={INPUT_CLS} required />

                </div>
                <button type="submit" disabled={loading} className={BTN_PRIMARY + ' disabled:opacity-60'}>
                  {loading ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
                  {loading ? 'Verifying…' : 'Verify & Sign in'}
                </button>
                <button type="button" onClick={() => { setOtpSent(false); setOtp(''); setDemoOtp('') }}
                  className="w-full text-xs text-ink-muted text-center py-1 hover:text-ink-secondary">
                  Change phone number
                </button>
              </form>
            )}
          </div>
        )}

        {/* Divider */}
        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 h-px bg-stone-200" />
          <span className="text-xs text-ink-faint">or</span>
          <div className="flex-1 h-px bg-stone-200" />
        </div>

        {/* Google mock */}
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
          Don't have an account?{' '}
          <Link to="/signup" className="font-semibold text-ink-secondary hover:text-ink-primary transition-colors">
            Sign up free
          </Link>
        </p>
      </div>
    </div>
  )
}
