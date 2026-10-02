import { useId, useState } from "react"
import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { TechChipList } from "../tech/TechChip"
import { Section } from "./Section"
import { ExperiencePlaceholder, LoadError } from "./Placeholders"
import { cardStyle } from "../../styles/surfaces"
import type { ExperienceDTO } from "../../types/content"

/** One role. Only the essentials show at first glance (dates, role, one
 *  context sentence); achievements and stack open on demand, so the section
 *  stays scannable. */
function ExperienceCard({ e }: { e: ExperienceDTO }) {
  const { lang } = useAppState()
  const L = t(lang)
  const [open, setOpen] = useState(false)
  const detailsId = useId()

  return (
    <article style={{ ...cardStyle, padding: "26px 30px", display: "flex", flexWrap: "wrap", gap: "12px 32px" }}>
      <div style={{ flex: "0 1 240px", display: "flex", flexDirection: "column", gap: 4 }}>
        <span style={{ fontFamily: "var(--mono)", fontSize: 14, color: "var(--ac)" }}>{e.period}</span>
        <span style={{ fontSize: 14, color: "var(--ink-2)" }}>
          {e.location} · {e.contract_type}
        </span>
      </div>
      <div style={{ flex: "1 1 520px", minWidth: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <h3 style={{ margin: 0, fontSize: 21, fontWeight: 700 }}>
          {e.role} · {e.company}
        </h3>
        <p style={{ margin: 0, fontSize: 16, lineHeight: 1.6, color: "var(--ink-2)", textWrap: "pretty" }}>{e.context}</p>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-controls={detailsId}
          style={{
            alignSelf: "flex-start",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "8px 14px",
            borderRadius: 10,
            border: "1px solid var(--stroke-2)",
            background: "transparent",
            fontFamily: "inherit",
            fontSize: 15,
            fontWeight: 600,
            color: "var(--ink)",
            cursor: "pointer",
          }}
        >
          {open ? L.hideDetails : L.showDetails}
          <span aria-hidden="true" style={{ display: "inline-block", transition: "transform .2s", transform: open ? "rotate(180deg)" : "none" }}>
            ▾
          </span>
        </button>
        <div id={detailsId} hidden={!open} style={{ animation: "pfFade .2s ease-out" }}>
          <ul className="text-list" style={{ margin: "4px 0 0", paddingLeft: 20, display: "flex", flexDirection: "column", gap: 8, fontSize: 16, lineHeight: 1.55 }}>
            {e.bullets.map((b) => (
              <li key={b} style={{ textWrap: "pretty" }}>
                {b}
              </li>
            ))}
          </ul>
          {e.stack.length > 0 && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 16, paddingTop: 14, borderTop: "1px solid var(--stroke)" }}>
              <span
                aria-hidden="true"
                style={{ fontFamily: "var(--mono)", fontSize: 12, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--ink-2)" }}
              >
                {L.stack}
              </span>
              <TechChipList skills={e.stack} size="sm" label={`${L.stackLabel}, ${e.company}`} />
            </div>
          )}
        </div>
      </div>
    </article>
  )
}

export function ExperienceSection() {
  const { lang, experience, contentStatus } = useAppState()
  const L = t(lang)
  const status = experience.length > 0 ? "ready" : contentStatus.experience

  return (
    <Section id="experience" title={L.navExperience}>
      {status === "loading" && <ExperiencePlaceholder />}
      {status === "error" && <LoadError />}
      {status === "ready" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {experience.map((e) => (
            <ExperienceCard key={e.company} e={e} />
          ))}
        </div>
      )}
    </Section>
  )
}
