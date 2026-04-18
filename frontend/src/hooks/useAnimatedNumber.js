import { useState, useEffect, useRef } from 'react'

/**
 * Animate a number from 0 to target with eased timing.
 * @param {number} target - The target number to animate to
 * @param {number} duration - Animation duration in ms (default 1200)
 * @returns {number} The current animated value
 */
export function useAnimatedNumber(target, duration = 1200) {
  const [current, setCurrent] = useState(0)
  const rafId = useRef(null)
  const startTime = useRef(null)

  useEffect(() => {
    if (target === 0 || target == null) {
      setCurrent(0)
      return
    }

    startTime.current = performance.now()

    const animate = (now) => {
      const elapsed = now - startTime.current
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCurrent(Math.round(eased * target))
      if (progress < 1) {
        rafId.current = requestAnimationFrame(animate)
      }
    }

    rafId.current = requestAnimationFrame(animate)
    return () => {
      if (rafId.current) cancelAnimationFrame(rafId.current)
    }
  }, [target, duration])

  return current
}

export default useAnimatedNumber
