import api from './api'

export const authAPI = {
  signup:    (data) => api.post('/auth/signup', data),
  login:     (data) => api.post('/auth/login', data),
  googleLogin:(data)=> api.post('/auth/google', data),
  sendOTP:   (phone)=> api.post('/auth/send-otp', { phone }),
  verifyOTP: (data) => api.post('/auth/verify-otp', data),
  getMe:     ()     => api.get('/auth/me'),
  logout:    ()     => api.post('/auth/logout'),
}

export const getToken  = ()       => localStorage.getItem('ra_token')
export const setToken  = (t)      => localStorage.setItem('ra_token', t)
export const clearToken= ()       => localStorage.removeItem('ra_token')
export const getUser   = ()       => { try { return JSON.parse(localStorage.getItem('ra_user') || 'null') } catch { return null } }
export const setUser   = (u)      => localStorage.setItem('ra_user', JSON.stringify(u))
export const clearUser = ()       => localStorage.removeItem('ra_user')
