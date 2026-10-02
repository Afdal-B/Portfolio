import type { CSSProperties, ReactNode } from "react"
import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { cardStyle } from "../../styles/surfaces"

/** Grey shapes standing in for a section's cards while its content loads,
 *  so the page keeps its layout instead of filling in all at once. */

function Bone({ width = "100%", height, radius, style }: { width?: string | number; height: number | string; radius?: number; style?: CSSProperties }) {
  return <span aria-hidden="true" className="skeleton" style={{ width, height, borderRadius: radius, ...style }} />
}

/** Wraps placeholders so assistive tech announces a load, not empty shapes. */
function Loading({ children }: { children: ReactNode }) {
  const { lang } = useAppState()
  return (
    <div role="status" aria-busy="true" aria-label={t(lang).loading}>
      {children}
    </div>
  )
}

export function LoadError() {
  const { lang } = useAppState()
  return (
    <p role="alert" style={{ ...cardStyle, margin: 0, padding: "18px 22px", fontSize: 16, color: "var(--ink-2)" }}>
      {t(lang).loadError}
    </p>
  )
}

export function ProjectsPlaceholder() {
  return (
    <Loading>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 20 }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{ ...cardStyle, flex: "1 1 320px", minWidth: 0, overflow: "hidden" }}>
            <Bone height="auto" radius={0} style={{ aspectRatio: "16/9" }} />
            <div style={{ padding: 22, display: "flex", flexDirection: "column", gap: 12 }}>
              <Bone width="40%" height={14} />
              <Bone width="85%" height={24} />
              <Bone height={16} />
              <Bone height={16} />
              <Bone width="70%" height={16} />
              <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                <Bone width={90} height={28} radius={999} />
                <Bone width={110} height={28} radius={999} />
                <Bone width={80} height={28} radius={999} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </Loading>
  )
}

export function ExperiencePlaceholder() {
  return (
    <Loading>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{ ...cardStyle, padding: "26px 30px", display: "flex", flexWrap: "wrap", gap: "12px 32px" }}>
            <div style={{ flex: "0 1 240px", display: "flex", flexDirection: "column", gap: 8 }}>
              <Bone width="80%" height={14} />
              <Bone width="60%" height={14} />
            </div>
            <div style={{ flex: "1 1 520px", minWidth: 0, display: "flex", flexDirection: "column", gap: 12 }}>
              <Bone width="55%" height={22} />
              <Bone height={16} />
              <Bone width="80%" height={16} />
              <Bone width={150} height={36} radius={10} />
            </div>
          </div>
        ))}
      </div>
    </Loading>
  )
}

export function SkillsPlaceholder() {
  const chips = [96, 120, 84, 110, 72, 130, 90]
  return (
    <Loading>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} style={{ ...cardStyle, flex: "1 1 460px", minWidth: 0, padding: 22, display: "flex", flexDirection: "column", gap: 14 }}>
            <Bone width="35%" height={18} />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {chips.map((width, j) => (
                <Bone key={j} width={width} height={36} radius={999} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </Loading>
  )
}
