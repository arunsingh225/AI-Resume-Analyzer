import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Smartphone, Mail, Scan } from 'lucide-react'
import { GoogleLogin } from '@react-oauth/google'
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
  const [otpSent,  setOtpSent]  = useState(false)

  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')
  const [slowHint, setSlowHint] = useState(false)

  const finish = (data) => {
    saveAuth(data)
    navigate('/', { replace: true })
  }

  // Show "server waking up" hint after 5 seconds of loading
  const withSlowHint = (fn) => async (...args) => {
    const timer = setTimeout(() => setSlowHint(true), 5000)
    try {
      return await fn(...args)
    } finally {
      clearTimeout(timer)
      setSlowHint(false)
    }
  }

  const handleEmail = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const r = await withSlowHint(() => authAPI.login({ email, password }))()
      finish(r.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally { setLoading(false) }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    setError(''); setLoading(true)
    try {
      // Send Google's JWT credential to backend for verification
      const r = await withSlowHint(() => 
        authAPI.googleLogin({ credential: credentialResponse.credential })
      )()
      finish(r.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Google login failed')
    } finally { setLoading(false) }
  }

  const handleGoogleError = () => {
    setError('Google sign-in was cancelled or failed. Please try again.')
  }

  const handleSendOTP = async () => {
    if (phone.length < 10) { setError('Enter a valid phone number'); return }
    setError(''); setLoading(true)
    try {
      await withSlowHint(() => authAPI.sendOTP(phone))()
      setOtpSent(true)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send OTP')
    } finally { setLoading(false) }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const r = await withSlowHint(() => authAPI.verifyOTP({ phone, otp }))()
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

        {/* Slow server hint */}
        {slowHint && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 text-sm flex items-center gap-2">
            <span className="w-4 h-4 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin flex-shrink-0" />
            Server is waking up (free tier). This takes ~15-30 seconds on first request…
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
                <button type="button" onClick={() => { setOtpSent(false); setOtp('') }}
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

        {/* Real Google Sign-In */}
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            theme="outline"
            size="large"
            width="100%"
            text="continue_with"
            shape="pill"
          />
        </div>

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
