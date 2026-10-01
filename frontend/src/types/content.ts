export interface ProjectDTO {
  meta: string
  title: string
  result: string
  problem: string
  method: string
  stack: string
  metrics: string
  image_seed: string
  image_url: string
  screenshots: string[]
  url: string
  /** Short card blurb (the backend falls back to `result`). */
  summary: string
  /** Source code or model page; empty when there is none. */
  code_url: string
  /** The stack resolved against the tech catalog, for logos. */
  stack_items: SkillDTO[]
}

export interface SkillDTO {
  name: string
  /** Key into TECH_ICONS (lib/techIcons.ts). */
  icon: string | null
  glyph: string[] | null
}

export interface SkillGroupDTO {
  id: string
  title: string
  skills: SkillDTO[]
}

/** Bilingual, id-carrying project record as stored by the admin API. The
 *  public /content/projects endpoint returns these already localized. */
export interface AdminProject {
  id: string
  meta: { fr: string; en: string }
  title: { fr: string; en: string }
  result: { fr: string; en: string }
  problem: { fr: string; en: string }
  method: { fr: string; en: string }
  stack: string
  metrics: { fr: string; en: string }
  url: string
  image_url: string
  screenshots: string[]
  image_seed: string
  summary: { fr: string; en: string }
  code_url: string
}

export interface ExperienceDTO {
  company: string
  role: string
  contract_type: string
  period: string
  location: string
  context: string
  bullets: string[]
  stack: SkillDTO[]
}

export interface ContactDTO {
  key: string
  value: string
  href: string
}

export interface SuggestionDTO {
  id: string
  label: string
}
