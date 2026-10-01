import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { mainImage } from "../../lib/projectImages"
import type { ReactNode } from "react"
import { codeLinkLabel } from "../../lib/projectLinks"
import { TechChipList } from "../tech/TechChip"

const blockStyle: React.CSSProperties = {
  padding: "14px 15px",
  borderRadius: 16,
  background: "var(--glass-2)",
  border: "1px solid var(--stroke)",
}

const kickerStyle: React.CSSProperties = {
  fontFamily: "var(--mono)",
  fontSize: 11.5,
  letterSpacing: ".1em",
  textTransform: "uppercase",
  color: "var(--ink-2)",
  marginBottom: 6,
}

export function ProjectModal() {
  const { lang, modal, projects, closeModal } = useAppState()
  const L = t(lang)
  if (modal == null) return null
  const p = projects[modal]
  if (!p) return null

  // Empty blocks are dropped: metrics, for one, are optional in the admin.
  const blocks: Array<{ k: string; v: ReactNode }> = [
    { k: L.problem, v: p.problem },
    { k: L.method, v: p.method },
    { k: L.stack, v: p.stack_items.length > 0 ? <TechChipList skills={p.stack_items} size="sm" label={L.stackLabel} /> : null },
    { k: L.metrics, v: p.metrics.trim() || null },
  ].filter((b) => b.v)

  return (
    <div
      onClick={closeModal}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 60,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        overflowY: "auto",
        background: "rgba(9,12,18,.42)",
        backdropFilter: "blur(10px)",
        animation: "pfFade .18s ease-out",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `url(${mainImage(p, 1200, 800)})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          filter: "blur(26px) saturate(115%)",
          transform: "scale(1.08)",
          opacity: 0.5,
        }}
      />
      <div
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        style={{
          position: "relative",
          width: "min(820px, 100%)",
          maxHeight: "calc(100vh - 48px)",
          overflowY: "auto",
          borderRadius: 26,
          border: "1px solid var(--stroke-2)",
          // Opaque: the blurred project image behind used to bleed through the text.
          background: "var(--panel)",
          boxShadow: "0 30px 80px rgba(9,12,18,.35)",
          animation: "pfIn .24s ease-out",
        }}
      >
        <div
          style={{
            display: "block",
            width: "100%",
            aspectRatio: "21/9",
            backgroundImage: `url(${mainImage(p, 1200, 514)})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            borderBottom: "1px solid var(--stroke)",
          }}
        />
        <div style={{ display: "flex", alignItems: "flex-start", gap: 14, padding: "18px 22px 16px" }}>
          <div style={{ flex: 1 }}>
            <div style={kickerStyle}>{p.meta}</div>
            <h2 style={{ fontSize: 24, lineHeight: 1.18, letterSpacing: "-.025em", fontWeight: 700, margin: 0, color: "var(--ink)", textWrap: "pretty" }}>
              {p.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={closeModal}
            aria-label={L.close}
            style={{ width: 34, height: 34, flex: "none", display: "grid", placeItems: "center", borderRadius: 12, border: "1px solid var(--stroke)", background: "var(--glass-2)", color: "var(--ink)", cursor: "pointer", fontSize: 15 }}
          >
            ✕
          </button>
        </div>
        <div style={{ padding: "4px 22px 4px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 12 }}>
          {blocks.map((b) => (
            <div key={b.k} style={blockStyle}>
              <div style={kickerStyle}>{b.k}</div>
              <div style={{ fontSize: 15, lineHeight: 1.55, color: "var(--ink)", textWrap: "pretty" }}>{b.v}</div>
            </div>
          ))}
        </div>
        <div style={{ padding: "16px 22px 4px" }}>
          <div style={{ padding: "14px 16px", borderRadius: 16, background: "var(--ac-soft)", border: "1px solid var(--ac-line)", fontSize: 16, lineHeight: 1.5, color: "var(--ink)", textWrap: "pretty" }}>
            {p.result}
          </div>
        </div>
        <div style={{ padding: "14px 22px 4px", display: "flex", gap: 10, flexWrap: "wrap" }}>
          <a
            href={p.url}
            target="_blank"
            rel="noopener"
            style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "11px 16px", borderRadius: 14, border: "1px solid var(--ac-line)", background: "var(--ac)", color: "var(--on-ac)", fontWeight: 600, fontSize: 15, textDecoration: "none" }}
          >
            {L.visit} <span aria-hidden="true">↗</span>
          </a>
          {p.code_url && (
            <a
              href={p.code_url}
              target="_blank"
              rel="noopener"
              style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "11px 16px", borderRadius: 14, border: "1px solid var(--stroke-2)", color: "var(--ink)", fontWeight: 600, fontSize: 15, textDecoration: "none" }}
            >
              {codeLinkLabel(p.code_url, L)} <span aria-hidden="true">↗</span>
            </a>
          )}
        </div>
        {p.screenshots.length > 0 ? (
          <div style={{ padding: "10px 22px 22px" }}>
            <div style={kickerStyle}>{L.shots}</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {p.screenshots.map((url) => (
                <span
                  key={url}
                  style={{
                    display: "block",
                    width: "100%",
                    aspectRatio: "16/9",
                    borderRadius: 14,
                    border: "1px solid var(--stroke)",
                    backgroundColor: "var(--glass-2)",
                    backgroundImage: `url(${url})`,
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                />
              ))}
            </div>
          </div>
        ) : (
          <div style={{ height: 18 }} />
        )}
      </div>
    </div>
  )
}
