import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { TechChipList } from "../tech/TechChip"
import { Section } from "./Section"
import { LoadError, SkillsPlaceholder } from "./Placeholders"
import { cardGrid, cardStyle } from "../../styles/surfaces"

export function SkillsSection() {
  const { lang, skillGroups, contentStatus } = useAppState()
  const L = t(lang)
  const status = skillGroups.length > 0 ? "ready" : contentStatus.skills

  if (status !== "ready") {
    return (
      <Section id="competences" title={L.navSkills}>
        {status === "loading" ? <SkillsPlaceholder /> : <LoadError />}
      </Section>
    )
  }

  return (
    <Section id="competences" title={L.navSkills}>
      <div style={cardGrid(460, 2, 16)}>
        {skillGroups.map((g) => (
          <div
            key={g.id}
            style={{ ...cardStyle, minWidth: 0, padding: 22, display: "flex", flexDirection: "column", gap: 14 }}
          >
            <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>{g.title}</h3>
            <TechChipList skills={g.skills} label={g.title} />
          </div>
        ))}
      </div>
    </Section>
  )
}
