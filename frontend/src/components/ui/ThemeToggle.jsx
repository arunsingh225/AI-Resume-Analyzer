import { useState, useEffect } from 'react'
import { Moon, Sun } from 'lucide-react'

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    if (typeof window === 'undefined') return false
    const saved = localStorage.getItem('ra_theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    const root = document.documentElement
    if (dark) {
      root.classList.add('dark')
      document.body.classList.add('dark')
    } else {
      root.classList.remove('dark')
      document.body.classList.remove('dark')
    }
    localStorage.setItem('ra_theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <button
      onClick={() => setDark(!dark)}
      className="w-9 h-9 rounded-xl flex items-center justify-center
        border border-stone-200 bg-white/80 backdrop-blur-sm
        hover:bg-stone-100 hover:border-stone-300
        transition-all duration-200 group"
      title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {dark ? (
        <Sun size={16} className="text-amber-500 group-hover:rotate-45 transition-transform" />
      ) : (
        <Moon size={16} className="text-slate-600 group-hover:-rotate-12 transition-transform" />
      )}
    </button>
  )
}
