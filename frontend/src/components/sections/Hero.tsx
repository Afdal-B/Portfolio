import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { PAGE_GUTTER, PAGE_WIDTH } from "../../styles/layout"
import { cardStyle } from "../../styles/surfaces"

const factLabel: React.CSSProperties = { fontSize: 14, color: "var(--ink-2)" }
const factValue: React.CSSProperties = { fontSize: 17, fontWeight: 600 }

const pill: React.CSSProperties = {
  padding: "6px 12px",
  borderRadius: 999,
  background: "var(--ac-soft)",
  border: "1px solid var(--ac-line)",
  color: "var(--ink)",
  fontSize: 14,
  fontWeight: 500,
}

export function Hero() {
  const { lang } = useAppState()
  const L = t(lang)

  return (
    <section
      aria-labelledby="hero-title"
      style={{
        maxWidth: PAGE_WIDTH,
        margin: "0 auto",
        padding: `72px ${PAGE_GUTTER}px 56px`,
        display: "flex",
        flexWrap: "wrap",
        gap: 40,
        alignItems: "center",
      }}
    >
      <div style={{ flex: "1 1 520px", minWidth: 0, display: "flex", flexDirection: "column", gap: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "7px 14px",
              borderRadius: 999,
              background: "var(--ac-soft)",
              border: "1px solid var(--ac-line)",
              color: "var(--ac)",
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            <span aria-hidden="true" style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--ac)" }} />
            {L.available}
          </span>
          <span style={{ fontFamily: "var(--mono)", fontSize: 13, color: "var(--ink-2)", letterSpacing: ".04em" }}>{L.location}</span>
        </div>
        <h1
          id="hero-title"
          style={{ margin: 0, fontSize: "clamp(36px, 5.4vw, 56px)", lineHeight: 1.06, letterSpacing: "-.03em", fontWeight: 800, textWrap: "balance" }}
        >
          {L.pitch}
        </h1>
        <p style={{ margin: 0, fontSize: 20, lineHeight: 1.55, color: "var(--ink-2)", maxWidth: "60ch" }}>{L.intro}</p>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
          <a
            href="#contact"
            style={{ padding: "15px 22px", borderRadius: 14, background: "var(--ac)", color: "var(--on-ac)", fontWeight: 700, fontSize: 16, textDecoration: "none" }}
          >
            {L.contactBtn}
          </a>
          <a
            href="#projets"
            style={{ padding: "15px 22px", borderRadius: 14, border: "1px solid var(--stroke-2)", color: "var(--ink)", fontWeight: 600, fontSize: 16, textDecoration: "none" }}
          >
            {L.seeProjects}
          </a>
          <a href="#assistant" style={{ padding: "15px 8px", color: "var(--ac)", fontWeight: 600, fontSize: 16, textDecoration: "none" }}>
            {L.askAssistant} <span aria-hidden="true">↓</span>
          </a>
        </div>
      </div>

      <aside
        aria-label={L.atAGlance}
        style={{ ...cardStyle, flex: "1 1 340px", minWidth: 0, padding: 26, display: "flex", flexDirection: "column", gap: 20 }}
      >
        <div style={{ fontFamily: "var(--mono)", fontSize: 13, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--ink-2)" }}>
          {L.atAGlance}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={factLabel}>{L.lastRoleLabel}</span>
          <span style={factValue}>{L.lastRole}</span>
          <span style={factLabel}>{L.lastRoleDetail}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={factLabel}>{L.educationLabel}</span>
          <span style={factValue}>{L.education}</span>
          <span style={factLabel}>{L.educationDetail}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <span style={factLabel}>{L.specialtiesLabel}</span>
          <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexWrap: "wrap", gap: 8 }}>
            {L.specialties.map((s) => (
              <li key={s} style={pill}>
                {s}
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </section>
  )
}
