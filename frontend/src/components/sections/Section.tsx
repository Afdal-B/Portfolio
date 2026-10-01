import type { ReactNode } from "react"
import { PAGE_GUTTER, PAGE_WIDTH } from "../../styles/layout"

/** A page section: anchor target, centred column, and a large heading. */
export function Section({
  id,
  title,
  aside,
  labelledBy,
  children,
}: {
  id: string
  title?: string
  /** Id of a heading rendered by the children, for sections without `title`. */
  labelledBy?: string
  aside?: ReactNode
  children: ReactNode
}) {
  const titleId = `${id}-title`
  return (
    <section
      id={id}
      aria-labelledby={title ? titleId : labelledBy}
      style={{ maxWidth: PAGE_WIDTH, margin: "0 auto", padding: `48px ${PAGE_GUTTER}px` }}
    >
      {title && (
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 16,
            flexWrap: "wrap",
            marginBottom: 28,
          }}
        >
          <h2 id={titleId} style={{ margin: 0, fontSize: "clamp(28px, 4vw, 36px)", letterSpacing: "-.02em", fontWeight: 800 }}>
            {title}
          </h2>
          {aside && <span style={{ fontSize: 16, color: "var(--ink-2)" }}>{aside}</span>}
        </div>
      )}
      {children}
    </section>
  )
}
