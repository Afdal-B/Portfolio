import { apiGet } from "./client"
import type { ContactDTO, ExperienceDTO, ProjectDTO, SkillGroupDTO, SuggestionDTO } from "../types/content"
import type { Lang } from "../types/chat"

export function getProjects(lang: Lang): Promise<ProjectDTO[]> {
  return apiGet<ProjectDTO[]>("/content/projects", { lang })
}

export function getExperience(lang: Lang): Promise<ExperienceDTO[]> {
  return apiGet<ExperienceDTO[]>("/content/experience", { lang })
}

export function getSkillGroups(lang: Lang): Promise<SkillGroupDTO[]> {
  return apiGet<SkillGroupDTO[]>("/content/skills", { lang })
}

export function getContacts(): Promise<ContactDTO[]> {
  return apiGet<ContactDTO[]>("/content/contacts")
}

export function getSuggestions(lang: Lang): Promise<SuggestionDTO[]> {
  return apiGet<SuggestionDTO[]>("/content/suggestions", { lang })
}
