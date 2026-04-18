import React from 'react'
import { useNavigate } from 'react-router-dom'
import Loader from '../components/Loader'

export default function AnalysisPage() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-base">
      <Loader step="Analyzing your resume…" fileName="" progress={0} />
    </div>
  )
}
