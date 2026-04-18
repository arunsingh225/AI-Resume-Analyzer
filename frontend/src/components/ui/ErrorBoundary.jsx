import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[300px] flex flex-col items-center justify-center p-8">
          <div className="w-14 h-14 rounded-2xl bg-warm-rose-bg flex items-center justify-center mb-4">
            <AlertTriangle size={24} className="text-warm-rose" />
          </div>
          <h3 className="font-display font-700 text-ink-primary text-lg mb-2">Something went wrong</h3>
          <p className="text-sm text-ink-muted mb-4 text-center max-w-sm">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="btn-secondary text-sm flex items-center gap-2"
          >
            <RefreshCw size={14} /> Try Again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
