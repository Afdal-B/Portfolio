import { Children, useCallback, useEffect, useRef, useState, type ReactNode } from "react"
import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { ROW_CARD_WIDTH } from "../../styles/surfaces"

const GAP = 20

const arrowStyle = (enabled: boolean): React.CSSProperties => ({
  width: 40,
  height: 40,
  display: "grid",
  placeItems: "center",
  borderRadius: 999,
  border: "1px solid var(--stroke-2)",
  background: "var(--panel)",
  color: "var(--ink)",
  fontSize: 17,
  cursor: enabled ? "pointer" : "default",
  opacity: enabled ? 1 : 0.35,
})

/** Projects on a single scrolling row, whatever their number, so the
 *  section keeps the same height as the catalog grows. Scrolls with the
 *  arrows, a trackpad, a finger or the keyboard, and snaps to each card. */
export function ProjectRow({ children }: { children: ReactNode }) {
  const { lang } = useAppState()
  const L = t(lang)
  const rowRef = useRef<HTMLDivElement>(null)
  const [canPrev, setCanPrev] = useState(false)
  const [canNext, setCanNext] = useState(false)

  const update = useCallback(() => {
    const row = rowRef.current
    if (!row) return
    setCanPrev(row.scrollLeft > 2)
    setCanNext(row.scrollLeft + row.clientWidth < row.scrollWidth - 2)
  }, [])

  useEffect(() => {
    update()
    const row = rowRef.current
    if (!row) return
    const observer = new ResizeObserver(update)
    observer.observe(row)
    return () => observer.disconnect()
  }, [update, children])

  const scrollByCard = (direction: -1 | 1) => {
    const row = rowRef.current
    const card = row?.firstElementChild as HTMLElement | null
    if (!row || !card) return
    row.scrollBy({ left: direction * (card.offsetWidth + GAP), behavior: "smooth" })
  }

  const scrollable = canPrev || canNext

  return (
    <div>
      {scrollable && (
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginBottom: 14 }}>
          <button type="button" aria-label={L.prevProjects} disabled={!canPrev} onClick={() => scrollByCard(-1)} style={arrowStyle(canPrev)}>
            ←
          </button>
          <button type="button" aria-label={L.nextProjects} disabled={!canNext} onClick={() => scrollByCard(1)} style={arrowStyle(canNext)}>
            →
          </button>
        </div>
      )}
      <div
        ref={rowRef}
        onScroll={update}
        role="region"
        aria-label={L.navProjects}
        // Focusable so keyboard users can scroll it with the arrow keys.
        tabIndex={scrollable ? 0 : -1}
        className="project-row"
        style={{
          display: "flex",
          gap: GAP,
          overflowX: "auto",
          scrollSnapType: "x mandatory",
          scrollPaddingInline: 2,
          // Room for card borders and the focus ring, which overflow:auto would clip.
          padding: "2px 2px 14px",
          margin: "-2px -2px 0",
        }}
      >
        {Children.map(children, (child) => (
          <div style={{ flex: `0 0 ${ROW_CARD_WIDTH}`, display: "flex", scrollSnapAlign: "start" }}>{child}</div>
        ))}
      </div>
    </div>
  )
}
