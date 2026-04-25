import axios from 'axios'
import { getToken, getRefreshToken, setToken, setRefreshToken, clearAllAuth } from './auth'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE, timeout: 60000 })

// Attach JWT automatically
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error)
    else prom.resolve(token)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const originalRequest = err.config

    // If 401 and we haven't already retried
    if (err.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = getRefreshToken()

      // No refresh token — redirect to login
      if (!refreshToken) {
        clearAllAuth()
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(err)
      }

      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const res = await axios.post(`${BASE}/auth/refresh`, {
          refresh_token: refreshToken
        })
        const { access_token, refresh_token } = res.data
        setToken(access_token)
        setRefreshToken(refresh_token)
        processQueue(null, access_token)
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshErr) {
        processQueue(refreshErr, null)
        clearAllAuth()
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(err)
  }
)

export default api

export const analyzeResume = async (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/api/resume/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => onProgress && onProgress(Math.round((e.loaded / e.total) * 100)),
  })
  return res.data
}

export const matchJD = (resumeText, jdText) =>
  api.post('/api/jd/match', { resume_text: resumeText, jd_text: jdText }).then(r => r.data)

export const improveResume = (resumeText) =>
  api.post('/api/improve/improve', { resume_text: resumeText }).then(r => r.data)

export const downloadJsonReport = async (data) => {
  const res = await api.post('/api/report/json', data, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a'); a.href = url; a.download = 'resume_analysis.json'; a.click()
  URL.revokeObjectURL(url)
}

export const downloadPdfReport = async (data) => {
  const res = await api.post('/api/report/pdf', data, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a'); a.href = url; a.download = 'resume_analysis.pdf'; a.click()
  URL.revokeObjectURL(url)
}

// ── Feedback ──
export const submitFeedback = (data) =>
  api.post('/api/feedback/', data).then(r => r.data)

export const getFeedbackHistory = (limit = 20) =>
  api.get(`/api/feedback/?limit=${limit}`).then(r => r.data)

// ── Analysis History ──
export const getHistory = (limit = 20, offset = 0) =>
  api.get(`/api/history/?limit=${limit}&offset=${offset}`).then(r => r.data)

export const getAnalysisDetail = (id) =>
  api.get(`/api/history/${id}`).then(r => r.data)

export const deleteAnalysis = (id) =>
  api.delete(`/api/history/${id}`).then(r => r.data)
