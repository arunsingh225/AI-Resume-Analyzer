export function Skeleton({ className = '', width, height, rounded = 'rounded-xl' }) {
  return (
    <div
      className={`shimmer-bg ${rounded} ${className}`}
      style={{ width: width || '100%', height: height || '1rem' }}
    />
  )
}

export function CardSkeleton({ lines = 3 }) {
  return (
    <div className="card p-5 space-y-3">
      <Skeleton height="0.75rem" width="40%" />
      <Skeleton height="2rem" width="30%" />
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} height="0.6rem" width={`${80 - i * 15}%`} />
      ))}
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-5 animate-fade-in">
      {/* Hero card skeleton */}
      <div className="glass p-6 flex flex-col sm:flex-row gap-6" style={{ padding: '1.5rem' }}>
        <Skeleton className="flex-shrink-0" width="152px" height="152px" rounded="rounded-full" />
        <div className="flex-1 space-y-3">
          <Skeleton height="1.5rem" width="60%" />
          <Skeleton height="0.75rem" width="40%" />
          <Skeleton height="0.75rem" width="80%" />
          <Skeleton height="0.75rem" width="55%" />
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[1, 2, 3, 4].map(i => <CardSkeleton key={i} lines={1} />)}
      </div>

      {/* Two column */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CardSkeleton lines={4} />
        <CardSkeleton lines={4} />
      </div>
    </div>
  )
}

export function RingSkeleton({ size = 152 }) {
  return (
    <div
      className="shimmer-bg rounded-full"
      style={{ width: `${size}px`, height: `${size}px` }}
    />
  )
}
