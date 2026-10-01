import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { PAGE_GUTTER, PAGE_WIDTH } from "../../styles/layout"

const segStyle = (active: boolean): React.CSSProperties => ({
  fontFamily: "var(--mono)",
  fontSize: 13,
  padding: "8px 10px",
  border: 0,
  borderRadius: 9,
  cursor: "pointer",
  background: active ? "var(--ink)" : "transparent",
  color: active ? "var(--page)" : "var(--ink-2)",
})

const navLinkStyle: React.CSSProperties = {
  padding: "10px 14px",
  borderRadius: 10,
  fontSize: 15,
  fontWeight: 500,
  color: "var(--ink)",
  textDecoration: "none",
}

export function Header() {
  const { lang, setLang, theme, toggleTheme } = useAppState()
  const L = t(lang)

  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 30,
        // Opaque, not glass: text over the animated background was hard to read.
        background: "var(--panel)",
        borderBottom: "1px solid var(--stroke-2)",
      }}
    >
      <div
        style={{
          maxWidth: PAGE_WIDTH,
          margin: "0 auto",
          padding: `14px ${PAGE_GUTTER}px`,
          display: "flex",
          alignItems: "center",
          gap: 16,
          flexWrap: "wrap",
        }}
      >
        <a href="#top" style={{ fontWeight: 700, fontSize: 18, color: "var(--ink)", textDecoration: "none", marginRight: "auto" }}>
          Afdal Bouraima
        </a>
        <nav className="site-nav" aria-label="Sections" style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          <a href="#projets" style={navLinkStyle}>
            {L.navProjects}
          </a>
          <a href="#experience" style={navLinkStyle}>
            {L.navExperience}
          </a>
          <a href="#competences" style={navLinkStyle}>
            {L.navSkills}
          </a>
          <a href="#assistant" style={{ ...navLinkStyle, color: "var(--ac)" }}>
            {L.navAssistant}
          </a>
        </nav>
        <div
          role="group"
          aria-label={L.langLabel}
          style={{ display: "flex", padding: 3, gap: 2, borderRadius: 12, border: "1px solid var(--stroke-2)" }}
        >
          <button type="button" onClick={() => setLang("fr")} aria-pressed={lang === "fr"} style={segStyle(lang === "fr")}>
            FR
          </button>
          <button type="button" onClick={() => setLang("en")} aria-pressed={lang === "en"} style={segStyle(lang === "en")}>
            EN
          </button>
        </div>
        <button
          type="button"
          onClick={toggleTheme}
          title={L.themeLabel}
          aria-label={L.themeLabel}
          style={{
            width: 40,
            height: 40,
            display: "grid",
            placeItems: "center",
            borderRadius: 12,
            border: "1px solid var(--stroke-2)",
            background: "transparent",
            cursor: "pointer",
            color: "var(--ink)",
            fontSize: 16,
          }}
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>
        <a
          href="#contact"
          style={{
            padding: "11px 18px",
            borderRadius: 12,
            background: "var(--ac)",
            color: "var(--on-ac)",
            fontWeight: 700,
            fontSize: 15,
            textDecoration: "none",
          }}
        >
          {L.contactBtn}
        </a>
      </div>
    </header>
  )
}
