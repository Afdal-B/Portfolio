import { useCallback, type RefObject } from "react"

/**
 * Scrolls the chat container so that #q-{index} sits near its top, retried at
 * 60/160/320/560ms since the DOM settles asynchronously after a state change
 * (ported from `scrollToQuestion` in the design prototype).
 */
export function useAutoScroll(containerRef: RefObject<HTMLElement | null>) {
  return useCallback(
    (index: number) => {
      if (index < 0) return
      const apply = () => {
        const c = containerRef.current
        if (!c) return
        const el = c.querySelector<HTMLElement>(`#q-${index}`)
        if (!el) return
        // Measured from bounding boxes rather than offsetTop, which depends on
        // which ancestor happens to be positioned now that the chat sits
        // inside a page section.
        const offset = el.getBoundingClientRect().top - c.getBoundingClientRect().top + c.scrollTop
        const target = Math.max(0, Math.min(offset - 12, c.scrollHeight - c.clientHeight))
        if (Math.abs(c.scrollTop - target) > 2) c.scrollTop = target
      }
      requestAnimationFrame(() => requestAnimationFrame(apply))
      ;[60, 160, 320, 560].forEach((t) => setTimeout(apply, t))
    },
    [containerRef],
  )
}
