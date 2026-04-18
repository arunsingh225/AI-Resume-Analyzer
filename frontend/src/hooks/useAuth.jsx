import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authAPI, getToken, setToken, setUser, getUser, clearToken, clearUser } from '../services/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUserState] = useState(getUser)
  const [loading, setLoading]   = useState(!!getToken())   // true only if token exists

  // Verify token on mount
  useEffect(() => {
    if (!getToken()) { setLoading(false); return }
    authAPI.getMe()
      .then(r => { setUserState(r.data); setUser(r.data) })
      .catch(() => { clearToken(); clearUser(); setUserState(null) })
      .finally(() => setLoading(false))
  }, [])

  const saveAuth = useCallback((token, userData) => {
    setToken(token)
    setUser(userData)
    setUserState(userData)
  }, [])

  const logout = useCallback(async () => {
    try { await authAPI.logout() } catch {}
    clearToken(); clearUser(); setUserState(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, saveAuth, logout, isLoggedIn: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
