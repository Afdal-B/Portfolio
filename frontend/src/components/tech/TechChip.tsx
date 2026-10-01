import { useAppState } from "../../context/AppStateContext"
import { TECH_ICONS } from "../../lib/techIcons"
import type { SkillDTO } from "../../types/content"

/** A technology's logo: a bundled brand logo when there is one, otherwise
 *  the line glyph the backend sends. Decorative, since the name is always
 *  printed next to it. */
export function TechIcon({ skill, size }: { skill: SkillDTO; size: number }) {
  const { theme } = useAppState()
  const icon = skill.icon ? TECH_ICONS[skill.icon] : undefined

  if (icon && "markup" in icon) {
    return (
      <svg
        width={size}
        height={size}
        viewBox={icon.viewBox}
        aria-hidden="true"
        style={{ flex: "none" }}
        // Static markup generated from Devicon into lib/techIcons.ts, never user input.
        dangerouslySetInnerHTML={{ __html: icon.markup }}
      />
    )
  }
  if (icon) {
    return (
      <svg width={size} height={size} viewBox={icon.viewBox} aria-hidden="true" style={{ flex: "none" }}>
        {icon.paths.map((p, i) => (
          <path key={i} d={p.d} fill={theme === "dark" ? p.dark : p.light} />
        ))}
      </svg>
    )
  }
  if (skill.glyph) {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="var(--ink-2)"
        strokeWidth={1.8}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
        style={{ flex: "none" }}
      >
        {skill.glyph.map((d, i) => (
          <path key={i} d={d} />
        ))}
      </svg>
    )
  }
  return null
}

export function TechChip({ skill, size = "md" }: { skill: SkillDTO; size?: "sm" | "md" }) {
  const sm = size === "sm"
  return (
    <li
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: sm ? 7 : 8,
        padding: sm ? "6px 11px" : "8px 13px",
        borderRadius: 999,
        border: "1px solid var(--stroke-2)",
        background: "var(--chip)",
        fontSize: sm ? 14 : 15,
        lineHeight: 1.2,
        color: "var(--ink)",
      }}
    >
      <TechIcon skill={skill} size={sm ? 16 : 18} />
      {skill.name}
    </li>
  )
}

export function TechChipList({ skills, size, label }: { skills: SkillDTO[]; size?: "sm" | "md"; label?: string }) {
  return (
    <ul aria-label={label} style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexWrap: "wrap", gap: 8 }}>
      {skills.map((s) => (
        <TechChip key={s.name} skill={s} size={size} />
      ))}
    </ul>
  )
}
