import api from './api'

export const authAPI = {
  signup:    (data) => api.post('/auth/signup', data),
  login:     (data) => api.post('/auth/login', data),
  googleLogin:(data)=> api.post('/auth/google', data),
  sendOTP:   (phone)=> api.post('/auth/send-otp', { phone }),
  verifyOTP: (data) => api.post('/auth/verify-otp', data),
  refresh:   (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  getMe:     ()     => api.get('/auth/me'),
  logout:    ()     => api.post('/auth/logout'),
}

// Access token (short-lived, 15 min)
export const getToken   = ()  => localStorage.getItem('ra_token')
export const setToken   = (t) => localStorage.setItem('ra_token', t)
export const clearToken = ()  => localStorage.removeItem('ra_token')

// Refresh token (long-lived, 7 days)
export const getRefreshToken  = ()  => localStorage.getItem('ra_refresh_token')
export const setRefreshToken  = (t) => localStorage.setItem('ra_refresh_token', t)
export const clearRefreshToken= ()  => localStorage.removeItem('ra_refresh_token')

// User info
export const getUser   = ()  => { try { return JSON.parse(localStorage.getItem('ra_user') || 'null') } catch { return null } }
export const setUser   = (u) => localStorage.setItem('ra_user', JSON.stringify(u))
export const clearUser = ()  => localStorage.removeItem('ra_user')

// Clear all auth state
export const clearAllAuth = () => {
  clearToken()
  clearRefreshToken()
  clearUser()
}
