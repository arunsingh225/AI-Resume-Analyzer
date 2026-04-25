import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import {
  authAPI,
  getToken, setToken, clearToken,
  setRefreshToken, clearRefreshToken,
  setUser, getUser, clearUser, clearAllAuth,
} from '../services/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUserState] = useState(getUser)
  const [loading, setLoading]   = useState(!!getToken())   // true only if token exists

  // Verify token on mount
  useEffect(() => {
    if (!getToken()) { setLoading(false); return }
    authAPI.getMe()
      .then(r => { setUserState(r.data); setUser(r.data) })
      .catch(() => { clearAllAuth(); setUserState(null) })
      .finally(() => setLoading(false))
  }, [])

  const saveAuth = useCallback((responseData) => {
    // responseData has { access_token, refresh_token, user }
    setToken(responseData.access_token)
    setRefreshToken(responseData.refresh_token)
    setUser(responseData.user)
    setUserState(responseData.user)
  }, [])

  const logout = useCallback(async () => {
    try { await authAPI.logout() } catch {}
    clearAllAuth()
    setUserState(null)
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
