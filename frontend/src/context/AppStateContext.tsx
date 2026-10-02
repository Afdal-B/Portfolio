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

/** Retries a content request: right after a quiet period the backend may
 *  need a moment to start, and a first attempt can fail while it does. */
async function withRetry<T>(load: () => Promise<T>, attempts = 3, delayMs = 1500): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try {
      return await load()
    } catch (err) {
      if (attempt >= attempts) throw err
      await sleep(delayMs * attempt)
    }
  }
}

export type LoadStatus = "loading" | "ready" | "error"

type ContentKey = "projects" | "experience" | "skills"

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
  /** Per page section, so each can show a placeholder until its content arrives. */
  contentStatus: Record<ContentKey, LoadStatus>
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
  const [contentStatus, setContentStatus] = useState<Record<ContentKey, LoadStatus>>({
    projects: "loading",
    experience: "loading",
    skills: "loading",
  })

  useEffect(() => {
    document.documentElement.setAttribute("data-pf", theme)
  }, [theme])

  useEffect(() => {
    let cancelled = false
    // On a language switch the previous content stays on screen until the
    // new one arrives: the placeholder is only for the very first load.
    const load = <T,>(key: ContentKey, request: () => Promise<T>, apply: (value: T) => void) =>
      withRetry(request)
        .then((value) => {
          if (cancelled) return
          apply(value)
          setContentStatus((prev) => ({ ...prev, [key]: "ready" }))
        })
        .catch(() => {
          if (cancelled) return
          setContentStatus((prev) => (prev[key] === "ready" ? prev : { ...prev, [key]: "error" }))
        })

    load("projects", () => getProjects(lang), setProjects)
    load("experience", () => getExperience(lang), setExperience)
    load("skills", () => getSkillGroups(lang), setSkillGroups)
    withRetry(() => getSuggestions(lang))
      .then((value) => !cancelled && setSuggestions(value))
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [lang])

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  useEffect(() => {
    withRetry(getContacts)
      .then(setContacts)
      .catch(() => {})
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
      contentStatus,
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
      contentStatus,
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
