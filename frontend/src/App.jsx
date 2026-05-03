import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { createContext, useContext, useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth'
import { ErrorBoundary } from './components/ui/ErrorBoundary'
import { ToastProvider } from './components/ui/Toast'
import LoginPage    from './pages/LoginPage'
import SignupPage   from './pages/SignupPage'
import HomePage     from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import DashboardPage from './pages/DashboardPage'

export const ResumeContext = createContext(null)
export const useResume = () => useContext(ResumeContext)

function ProtectedRoute({ children }) {
  const { isLoggedIn, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#EDECEA' }}>
      <div className="flex gap-2">
        {[0,1,2].map(i => (
          <div key={i} className="w-3 h-3 rounded-full bg-stone-400 animate-bounce"
            style={{ animationDelay: `${i*0.15}s` }} />
        ))}
      </div>
    </div>
  )
  return isLoggedIn ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const { isLoggedIn, loading } = useAuth()
  // Show spinner instead of null — prevents blank white screen during auth check
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#EDECEA' }}>
      <div className="flex gap-2">
        {[0,1,2].map(i => (
          <div key={i} className="w-3 h-3 rounded-full bg-stone-400 animate-bounce"
            style={{ animationDelay: `${i*0.15}s` }} />
        ))}
      </div>
    </div>
  )
  return isLoggedIn ? <Navigate to="/" replace /> : children
}

export default function App() {
  // ── Persist analysis result in localStorage ──
  const [result, setResult] = useState(() => {
    try {
      const saved = localStorage.getItem('ra_analysis')
      return saved ? JSON.parse(saved) : null
    } catch { return null }
  })
  const [file, setFile] = useState(null)

  useEffect(() => {
    if (result) {
      try {
        localStorage.setItem('ra_analysis', JSON.stringify(result))
      } catch { /* quota exceeded — silently fail */ }
    } else {
      localStorage.removeItem('ra_analysis')
    }
  }, [result])

  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <ResumeContext.Provider value={{ result, setResult, file, setFile }}>
            <Routes>
              <Route path="/login"  element={<PublicRoute><LoginPage /></PublicRoute>} />
              <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
              <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
              <Route path="/analyzing" element={<ProtectedRoute><AnalysisPage /></ProtectedRoute>} />
              <Route path="/dashboard/*" element={
                <ProtectedRoute>
                  {result ? <DashboardPage /> : <Navigate to="/" replace />}
                </ProtectedRoute>
              } />
            </Routes>
          </ResumeContext.Provider>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

