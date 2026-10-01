import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { TechChipList } from "../tech/TechChip"
import { Section } from "./Section"
import { cardStyle } from "../../styles/surfaces"

export function SkillsSection() {
  const { lang, skillGroups } = useAppState()
  const L = t(lang)

  return (
    <Section id="competences" title={L.navSkills}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
        {skillGroups.map((g) => (
          <div
            key={g.id}
            style={{ ...cardStyle, flex: "1 1 460px", minWidth: 0, padding: 22, display: "flex", flexDirection: "column", gap: 14 }}
          >
            <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>{g.title}</h3>
            <TechChipList skills={g.skills} label={g.title} />
          </div>
        ))}
      </div>
    </Section>
  )
}
