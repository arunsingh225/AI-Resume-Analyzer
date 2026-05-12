import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import {
  authAPI,
  getToken, setToken, clearToken,
  setRefreshToken, clearRefreshToken,
  setUser, getUser, clearUser, clearAllAuth,
} from '../services/auth'

const AuthContext = createContext(null)

// Admin email whitelist — only these users see the Admin Dashboard nav item
const ADMIN_EMAILS = ['arish22516@gmail.com']

export function AuthProvider({ children }) {
  const [user,    setUserState] = useState(getUser)
  const [loading, setLoading]   = useState(!!getToken())

  useEffect(() => {
    if (!getToken()) { setLoading(false); return }
    authAPI.getMe()
      .then(r => { setUserState(r.data); setUser(r.data) })
      .catch(() => { clearAllAuth(); setUserState(null) })
      .finally(() => setLoading(false))
  }, [])

  const saveAuth = useCallback((responseData) => {
    setToken(responseData.access_token)
    setRefreshToken(responseData.refresh_token)
    setUser(responseData.user)
    setUserState(responseData.user)
  }, [])

  const logout = useCallback(() => {
    clearAllAuth()
    setUserState(null)
    authAPI.logout().catch(() => {})
  }, [])

  const isAdmin = ADMIN_EMAILS.includes(user?.email)

  return (
    <AuthContext.Provider value={{ user, loading, saveAuth, logout, isLoggedIn: !!user, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
