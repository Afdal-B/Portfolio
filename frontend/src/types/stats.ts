export type QuestionOutcome = "rag" | "scripted" | "limited"

export interface DailyStats {
  day: string
  page_views: number
  visitors: number
  questions: Partial<Record<QuestionOutcome, number>>
}

export interface QuestionRecord {
  at: string
  outcome: QuestionOutcome
  text: string
  lang: string
  confidence: number | null
}

export interface Stats {
  days: DailyStats[]
  countries: Record<string, number>
  cities: Record<string, number>
  referrers: Record<string, number>
  recent_questions: QuestionRecord[]
  persistent: boolean
}

export interface AdminCapabilities {
  projects_editable: boolean
}
