/** Shared surface styles for the page sections. */

export const cardStyle: React.CSSProperties = {
  borderRadius: 20,
  background: "var(--panel)",
  border: "1px solid var(--stroke-2)",
}

export const kickerStyle: React.CSSProperties = {
  fontFamily: "var(--mono)",
  fontSize: 13,
  letterSpacing: ".06em",
  textTransform: "uppercase",
  color: "var(--ac)",
}

/** A grid of equal-width cards: as many columns as fit at `minWidth`, never
 *  more than `maxColumns`, a single column on narrow screens. Unlike a
 *  wrapping flex row, a card left alone on the last row keeps the width of
 *  the others instead of stretching across the page. */
export function cardGrid(minWidth: number, maxColumns: number, gap = 20): React.CSSProperties {
  const share = `calc((100% - ${(maxColumns - 1) * gap}px) / ${maxColumns})`
  return {
    display: "grid",
    gridTemplateColumns: `repeat(auto-fill, minmax(max(min(100%, ${minWidth}px), ${share}), 1fr))`,
    gap,
  }
}
