export type Lang = "fr" | "en"
export type Theme = "light" | "dark"
export type Intent =
  | "profile"
  | "avail"
  | "projects"
  | "skills"
  | "experience"
  | "nocv"
  | "contact"
  | "team"
  | "fallback"
export type Engine = "scripted" | "rag"

export interface ChatResponse {
  answer: string
  sources: string[] | null
  confidence: number | null
  intent: Intent
  engine: Engine
}

export interface AskedItem {
  q: string
  a: string
  sources: string[] | null
  confidence: number | null
  engine?: Engine
}

export interface Message {
  domId: string
  isBot: boolean
  text: string
  isPending: boolean
  askedIndex?: number
}
