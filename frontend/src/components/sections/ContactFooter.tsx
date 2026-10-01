import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { PAGE_GUTTER, PAGE_WIDTH } from "../../styles/layout"

export function ContactFooter() {
  const { lang, contacts } = useAppState()
  const L = t(lang)
  const email = contacts.find((c) => c.href.startsWith("mailto:"))
  const others = contacts.filter((c) => c !== email)

  return (
    <footer
      id="contact"
      aria-labelledby="contact-title"
      style={{ borderTop: "1px solid var(--stroke-2)", background: "var(--panel)", marginTop: 48 }}
    >
      <div
        style={{
          maxWidth: PAGE_WIDTH,
          margin: "0 auto",
          padding: `56px ${PAGE_GUTTER}px`,
          display: "flex",
          flexWrap: "wrap",
          gap: 28,
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ flex: "1 1 380px", display: "flex", flexDirection: "column", gap: 10 }}>
          <h2 id="contact-title" style={{ margin: 0, fontSize: "clamp(28px, 4vw, 34px)", letterSpacing: "-.02em", fontWeight: 800 }}>
            {L.contactTitle}
          </h2>
          <p style={{ margin: 0, fontSize: 17, color: "var(--ink-2)" }}>{L.contactLead}</p>
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {email && (
            <a
              href={email.href}
              style={{
                padding: "14px 20px",
                borderRadius: 14,
                background: "var(--ac)",
                color: "var(--on-ac)",
                fontWeight: 700,
                fontSize: 16,
                textDecoration: "none",
                overflowWrap: "anywhere",
              }}
            >
              {email.value}
            </a>
          )}
          {others.map((c) => (
            <a
              key={c.key}
              href={c.href}
              target="_blank"
              rel="noopener"
              style={{
                padding: "14px 20px",
                borderRadius: 14,
                border: "1px solid var(--stroke-2)",
                color: "var(--ink)",
                fontWeight: 600,
                fontSize: 16,
                textDecoration: "none",
              }}
            >
              {c.key} <span aria-hidden="true">↗</span>
            </a>
          ))}
        </div>
      </div>
    </footer>
  )
}
