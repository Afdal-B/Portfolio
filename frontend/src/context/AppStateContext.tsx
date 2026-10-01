import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { ReactNode } from "react"
import { postChat } from "../api/chat"
import { ApiError } from "../api/client"
import { getContacts, getExperience, getProjects, getSkillGroups, getSuggestions } from "../api/content"
import { t } from "../i18n/copy"
import type { AskedItem, Lang, Theme } from "../types/chat"
import type { ContactDTO, ExperienceDTO, ProjectDTO, SkillGroupDTO, SuggestionDTO } from "../types/content"

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

interface AppState {
  lang: Lang
  theme: Theme
  draft: string
  asked: AskedItem[]
  traces: Record<number, boolean>
  modal: number | null
  pending: boolean
  projects: ProjectDTO[]
  experience: ExperienceDTO[]
  skillGroups: SkillGroupDTO[]
  contacts: ContactDTO[]
  suggestions: SuggestionDTO[]
  setLang: (lang: Lang) => void
  toggleTheme: () => void
  setDraft: (draft: string) => void
  ask: (text: string) => void
  toggleTrace: (index: number) => void
  openModal: (index: number) => void
  closeModal: () => void
}

const AppStateCtx = createContext<AppState | null>(null)

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("fr")
  const [theme, setThemeState] = useState<Theme>("dark")
  const [draft, setDraft] = useState("")
  const [asked, setAsked] = useState<AskedItem[]>([])
  const [traces, setTraces] = useState<Record<number, boolean>>({})
  const [modal, setModal] = useState<number | null>(null)
  const [pending, setPending] = useState(false)

  const [projects, setProjects] = useState<ProjectDTO[]>([])
  const [experience, setExperience] = useState<ExperienceDTO[]>([])
  const [skillGroups, setSkillGroups] = useState<SkillGroupDTO[]>([])
  const [contacts, setContacts] = useState<ContactDTO[]>([])
  const [suggestions, setSuggestions] = useState<SuggestionDTO[]>([])

  useEffect(() => {
    document.documentElement.setAttribute("data-pf", theme)
  }, [theme])

  useEffect(() => {
    getProjects(lang).then(setProjects)
    getExperience(lang).then(setExperience)
    getSuggestions(lang).then(setSuggestions)
    getSkillGroups(lang).then(setSkillGroups)
  }, [lang])

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  useEffect(() => {
    getContacts().then(setContacts)
  }, [])

  useEffect(() => {
    const esc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setModal(null)
    }
    window.addEventListener("keydown", esc)
    return () => window.removeEventListener("keydown", esc)
  }, [])

  const toggleTheme = useCallback(() => {
    setThemeState((t) => (t === "dark" ? "light" : "dark"))
  }, [])

  const ask = useCallback(
    (text: string) => {
      const trimmed = text.trim()
      if (!trimmed) return
      const index = asked.length
      setAsked((prev) => [...prev, { q: trimmed, a: "", sources: null, confidence: null }])
      setDraft("")
      setPending(true)

      const minDelay = sleep(700 + Math.round(Math.random() * 450))
      const call = postChat(trimmed, lang)

      Promise.all([call, minDelay])
        .then(([res]) => ({
          q: trimmed,
          a: res.answer,
          sources: res.sources,
          confidence: res.confidence,
          engine: res.engine,
        }))
        // Without this, a failed request (backend restarting, network drop)
        // left the typing dots spinning forever.
        .catch((err: unknown): AskedItem => {
          const limited = err instanceof ApiError && err.status === 429
          return { q: trimmed, a: limited ? t(lang).rateLimited : t(lang).requestFailed, sources: null, confidence: null }
        })
        .then((item) => {
          setAsked((prev) => {
            const next = [...prev]
            next[index] = item
            return next
          })
          setPending(false)
        })
    },
    [asked.length, lang],
  )

  const toggleTrace = useCallback((index: number) => {
    setTraces((prev) => ({ ...prev, [index]: !prev[index] }))
  }, [])

  const value = useMemo<AppState>(
    () => ({
      lang,
      theme,
      draft,
      asked,
      traces,
      modal,
      pending,
      projects,
      experience,
      skillGroups,
      contacts,
      suggestions,
      setLang,
      toggleTheme,
      setDraft,
      ask,
      toggleTrace,
      openModal: setModal,
      closeModal: () => setModal(null),
    }),
    [
      lang,
      theme,
      draft,
      asked,
      traces,
      modal,
      pending,
      projects,
      experience,
      skillGroups,
      contacts,
      suggestions,
      toggleTheme,
      ask,
      toggleTrace,
    ],
  )

  return <AppStateCtx.Provider value={value}>{children}</AppStateCtx.Provider>
}

export function useAppState(): AppState {
  const ctx = useContext(AppStateCtx)
  if (!ctx) throw new Error("useAppState must be used within AppStateProvider")
  return ctx
}
