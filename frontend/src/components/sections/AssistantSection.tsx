import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { ChatFrame } from "../chat/ChatFrame"
import { Section } from "./Section"
import { kickerStyle } from "../../styles/surfaces"

export function AssistantSection() {
  const { lang } = useAppState()
  const L = t(lang)

  return (
    <Section id="assistant" labelledBy="assistant-title">
      <div
        style={{
          padding: "clamp(20px, 2.5vw, 28px)",
          borderRadius: 24,
          background: "var(--panel)",
          border: "1px solid var(--ac-line)",
          display: "flex",
          flexWrap: "wrap",
          gap: 36,
        }}
      >
        <div style={{ flex: "1 1 560px", minWidth: 0, display: "flex", flexDirection: "column", gap: 14 }}>
          <span style={kickerStyle}>{L.assistantKicker}</span>
          <h2 id="assistant-title" style={{ margin: 0, fontSize: "clamp(26px, 3.6vw, 34px)", letterSpacing: "-.02em", fontWeight: 800, textWrap: "balance" }}>
            {L.assistantTitle}
          </h2>
          <ChatFrame />
        </div>
        <aside aria-labelledby="build-title" style={{ flex: "1 1 300px", minWidth: 0, display: "flex", flexDirection: "column", gap: 16 }}>
          <h3 id="build-title" style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>
            {L.buildTitle}
          </h3>
          <p style={{ margin: 0, fontSize: 16, lineHeight: 1.55, color: "var(--ink-2)" }}>{L.buildLead}</p>
          <ol className="text-list" style={{ margin: 0, paddingLeft: 22, display: "flex", flexDirection: "column", gap: 10, fontSize: 16, lineHeight: 1.5 }}>
            {L.buildSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </aside>
      </div>
    </Section>
  )
}
