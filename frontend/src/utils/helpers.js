/* ── Score / grade helpers ─────────────────────────────────────── */
export const scoreColor = (v) => {
  if (v >= 75) return '#4E7245'  // sage green
  if (v >= 55) return '#9E6F1A'  // warm amber
  return '#9B3A3A'               // muted rose
}

export const scoreBgColor = (v) => {
  if (v >= 75) return '#F3F6F1'
  if (v >= 55) return '#FAF0D7'
  return '#FDF4F4'
}

export const gradeRingColor = scoreColor  // alias

export const gradeBadgeClass = (grade) => {
  if (grade === 'A') return 'badge-sage'
  if (grade === 'B') return 'badge-slate'
  if (grade === 'C') return 'badge-amber'
  return 'badge-rose'
}

export const matchColor = (pct) => {
  if (pct >= 78) return '#4E7245'
  if (pct >= 58) return '#9E6F1A'
  return '#9B3A3A'
}

/* ── Level helpers ─────────────────────────────────────────────── */
export const levelLabel = (lvl) => {
  const m = { fresher: 'Fresher', junior: 'Junior', mid: 'Mid-Level', senior: 'Senior' }
  return m[lvl] || (lvl ? lvl.charAt(0).toUpperCase() + lvl.slice(1) : 'N/A')
}

export const levelBadgeClass = (lvl) => {
  const m = {
    fresher: 'badge-slate',
    junior:  'badge-slate',
    mid:     'badge-sage',
    senior:  'badge-amber',
  }
  return m[lvl] || 'badge-stone'
}

/* ── Score bar colors — neutral palette ────────────────────────── */
export const scoreBarColor = (key) => {
  const m = {
    keyword_score:    '#4E7245',  // sage
    formatting_score: '#57534E',  // stone
    section_score:    '#9E6F1A',  // amber
    experience_score: '#4B5570',  // slate
    skill_score:      '#9B3A3A',  // rose
  }
  return m[key] || '#57534E'
}

/* ── Platform badge style for CourseCard ──────────────────────── */
export const platformBadgeStyle = (platform = '') => {
  const p = platform.toLowerCase()
  if (p.includes('coursera'))   return { bg: '#0056D2', text: '#fff' }
  if (p.includes('udemy'))      return { bg: '#9B4DE0', text: '#fff' }
  if (p.includes('linkedin'))   return { bg: '#0A66C2', text: '#fff' }
  if (p.includes('google') || p.includes('skillshop')) return { bg: '#4285F4', text: '#fff' }
  if (p.includes('edx') || p.includes('harvard'))      return { bg: '#02262B', text: '#fff' }
  if (p.includes('cfi') || p.includes('corporate finance')) return { bg: '#003366', text: '#fff' }
  if (p.includes('hubspot'))    return { bg: '#FF7A59', text: '#fff' }
  if (p.includes('educative'))  return { bg: '#1A1A2E', text: '#fff' }
  if (p.includes('citi'))       return { bg: '#007CBA', text: '#fff' }
  if (p.includes('microsoft'))  return { bg: '#004880', text: '#fff' }
  return { bg: '#44403C', text: '#fff' }
}

/* ── Misc ──────────────────────────────────────────────────────── */
export const truncate = (str, n = 60) => str?.length > n ? str.slice(0, n) + '…' : str

export const clamp = (v, min, max) => Math.min(Math.max(v, min), max)
