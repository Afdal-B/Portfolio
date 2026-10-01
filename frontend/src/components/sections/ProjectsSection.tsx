import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { mainImage } from "../../lib/projectImages"
import { codeLinkLabel } from "../../lib/projectLinks"
import { TechChipList } from "../tech/TechChip"
import type { ProjectDTO } from "../../types/content"
import { Section } from "./Section"
import { cardStyle, kickerStyle } from "../../styles/surfaces"

/** How many stack items a card shows; the modal lists them all. */
const CARD_TAGS = 3

/** Clamps text to `lines` and reserves that height even when the text is
 *  shorter, so titles, blurbs and the rows below line up across cards. */
function clamp(lines: number, fontSize: number, lineHeight: number): React.CSSProperties {
  return {
    display: "-webkit-box",
    WebkitBoxOrient: "vertical",
    WebkitLineClamp: lines,
    overflow: "hidden",
    fontSize,
    lineHeight,
    minHeight: `${lines * lineHeight}em`,
  }
}

function ProjectCard({ project, index }: { project: ProjectDTO; index: number }) {
  const { lang, openModal } = useAppState()
  const L = t(lang)
  const hasDemo = project.url && project.url !== "#"

  return (
    <article style={{ ...cardStyle, flex: "1 1 320px", minWidth: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <img
        src={mainImage(project, 960, 540)}
        alt={L.imageAlt(project.title)}
        loading="lazy"
        style={{ display: "block", width: "100%", aspectRatio: "16/9", objectFit: "cover", borderBottom: "1px solid var(--stroke-2)" }}
      />
      <div style={{ padding: 22, display: "flex", flexDirection: "column", gap: 12, flexGrow: 1 }}>
        <span style={kickerStyle}>{project.meta}</span>
        <h3 title={project.title} style={{ margin: 0, fontWeight: 700, textWrap: "pretty", ...clamp(2, 22, 1.25) }}>
          {project.title}
        </h3>
        <p style={{ margin: 0, color: "var(--ink-2)", textWrap: "pretty", ...clamp(3, 16, 1.55) }}>{project.summary}</p>
        <TechChipList skills={project.stack_items.slice(0, CARD_TAGS)} size="sm" label={L.stackLabel} />
        <div style={{ display: "flex", gap: 18, marginTop: "auto", paddingTop: 8, flexWrap: "wrap", alignItems: "center" }}>
          {hasDemo && (
            <a href={project.url} target="_blank" rel="noopener" style={{ fontWeight: 700, fontSize: 16, textDecoration: "none" }}>
              {L.demo} <span aria-hidden="true">↗</span>
            </a>
          )}
          {project.code_url && (
            <a href={project.code_url} target="_blank" rel="noopener" style={{ fontWeight: 600, fontSize: 16, color: "var(--ink)", textDecoration: "none" }}>
              {codeLinkLabel(project.code_url, L)} <span aria-hidden="true">↗</span>
            </a>
          )}
          <button
            type="button"
            onClick={() => openModal(index)}
            style={{
              marginLeft: "auto",
              padding: 0,
              border: 0,
              background: "none",
              fontFamily: "inherit",
              fontWeight: 600,
              fontSize: 16,
              color: "var(--ink-2)",
              textDecoration: "underline",
              textUnderlineOffset: 3,
              cursor: "pointer",
            }}
          >
            {L.details}
          </button>
        </div>
      </div>
    </article>
  )
}

export function ProjectsSection() {
  const { lang, projects } = useAppState()
  const L = t(lang)

  return (
    <Section id="projets" title={L.navProjects} aside={L.projectsLead}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 20 }}>
        {projects.map((p, i) => (
          <ProjectCard key={p.title} project={p} index={i} />
        ))}
      </div>
    </Section>
  )
}
