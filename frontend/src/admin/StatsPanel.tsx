import { useEffect, useMemo, useState } from "react"
import { AdminAuthError, getStats } from "../api/admin"
import { isOwner, setOwner } from "../lib/owner"
import type { DailyStats, QuestionOutcome, Stats } from "../types/stats"
import { Banner } from "./ui"
import { card, secondaryBtn } from "./styles"

const PERIODS = [7, 30, 90]

const OUTCOMES: Array<{ key: QuestionOutcome; label: string; color: string }> = [
  { key: "rag", label: "Générées par l'IA", color: "var(--ac)" },
  { key: "scripted", label: "Scriptées", color: "#8a96a3" },
  { key: "limited", label: "Limite atteinte", color: "#e07a5f" },
]

const countryNames = new Intl.DisplayNames(["fr"], { type: "region" })

function countryName(code: string): string {
  try {
    return countryNames.of(code) ?? code
  } catch {
    return code
  }
}

function sum(values: number[]): number {
  return values.reduce((total, value) => total + value, 0)
}

function shortDay(day: string): string {
  const [, month, date] = day.split("-")
  return `${date}/${month}`
}

export function StatsPanel({ token, onAuthError }: { token: string; onAuthError: () => void }) {
  const [days, setDays] = useState(30)
  const [stats, setStats] = useState<Stats | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [excluded, setExcluded] = useState(isOwner)

  useEffect(() => {
    let cancelled = false
    getStats(token, days)
      .then((loaded) => {
        if (cancelled) return
        setStats(loaded)
        setError(null)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "Erreur inconnue")
        if (err instanceof AdminAuthError) onAuthError()
      })
    return () => {
      cancelled = true
    }
  }, [token, days, onAuthError])

  const toggleExcluded = () => {
    setOwner(!excluded)
    setExcluded(!excluded)
  }

  const totals = useMemo(() => {
    if (!stats) return null
    const questions = (key: QuestionOutcome) => sum(stats.days.map((d) => d.questions[key] ?? 0))
    const rag = questions("rag")
    const scripted = questions("scripted")
    return {
      pageViews: sum(stats.days.map((d) => d.page_views)),
      visitors: sum(stats.days.map((d) => d.visitors)),
      questions: rag + scripted + questions("limited"),
      aiShare: rag + scripted > 0 ? Math.round((100 * rag) / (rag + scripted)) : null,
    }
  }, [stats])

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 18 }}>
        <div role="group" aria-label="Période" style={{ display: "flex", gap: 6 }}>
          {PERIODS.map((period) => (
            <button
              key={period}
              type="button"
              onClick={() => setDays(period)}
              aria-pressed={days === period}
              style={{
                ...secondaryBtn,
                ...(days === period ? { background: "var(--ac-soft)", borderColor: "var(--ac-line)", color: "var(--ac)" } : {}),
              }}
            >
              {period} jours
            </button>
          ))}
        </div>
        <label style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8, fontSize: 14, cursor: "pointer" }}>
          <input type="checkbox" checked={excluded} onChange={toggleExcluded} />
          Exclure ce navigateur des statistiques
        </label>
      </div>

      {error && <Banner tone="error">{error}</Banner>}
      {stats && !stats.persistent && (
        <Banner tone="info">
          Les statistiques sont gardées en mémoire sur ce serveur : elles repartent de zéro à chaque redémarrage.
          Configurez Upstash Redis pour les conserver.
        </Banner>
      )}

      {!stats || !totals ? (
        <p style={{ color: "var(--ink-2)" }}>Chargement…</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
            <Kpi label="Pages vues" value={totals.pageViews} />
            <Kpi label="Visiteurs uniques" value={totals.visitors} hint="comptés par jour, puis additionnés" />
            <Kpi label="Questions à l'assistant" value={totals.questions} />
            <Kpi
              label="Réponses générées par l'IA"
              value={totals.aiShare == null ? "–" : `${totals.aiShare} %`}
              hint="le reste : réponses scriptées"
            />
          </div>

          <section style={card}>
            <h2 style={sectionTitle}>Visites par jour</h2>
            <Legend items={[{ label: "Pages vues", color: "var(--ink-3)" }, { label: "Visiteurs uniques", color: "var(--ac)" }]} />
            <BarChart
              days={stats.days}
              series={[
                { label: "Pages vues", color: "var(--ink-3)", value: (d) => d.page_views },
                { label: "Visiteurs uniques", color: "var(--ac)", value: (d) => d.visitors },
              ]}
              mode="overlay"
            />
          </section>

          <section style={card}>
            <h2 style={sectionTitle}>Questions à l'assistant par jour</h2>
            <Legend items={OUTCOMES} />
            <BarChart
              days={stats.days}
              series={OUTCOMES.map((o) => ({ label: o.label, color: o.color, value: (d: DailyStats) => d.questions[o.key] ?? 0 }))}
              mode="stack"
            />
          </section>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
            <Ranking title="Pays" entries={stats.countries} format={countryName} />
            <Ranking title="Villes" entries={stats.cities} />
            <Ranking
              title="Provenance"
              entries={stats.referrers}
              format={(host) => (host === "direct" ? "Accès direct" : host)}
            />
          </div>

          <section style={card}>
            <h2 style={sectionTitle}>Dernières questions</h2>
            <p style={{ margin: "0 0 12px", fontSize: 13, color: "var(--ink-2)" }}>Conservées 90 jours.</p>
            {stats.recent_questions.length === 0 ? (
              <p style={{ margin: 0, color: "var(--ink-2)", fontSize: 14 }}>Aucune question sur la période.</p>
            ) : (
              <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
                {stats.recent_questions.map((q, i) => {
                  const outcome = OUTCOMES.find((o) => o.key === q.outcome)
                  return (
                    <li key={`${q.at}-${i}`} style={{ display: "flex", gap: 12, alignItems: "baseline", fontSize: 14 }}>
                      <span style={{ flex: "none", width: 92, fontFamily: "var(--mono)", fontSize: 12, color: "var(--ink-2)" }}>
                        {new Date(q.at).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}
                      </span>
                      <span style={{ flex: 1, minWidth: 0, overflowWrap: "anywhere" }}>{q.text}</span>
                      <span style={{ flex: "none", fontSize: 12, color: outcome?.color }}>
                        {outcome?.key === "rag" ? "IA" : outcome?.label}
                        {q.confidence != null && ` · ${q.confidence} %`}
                      </span>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>
        </div>
      )}
    </>
  )
}

const sectionTitle: React.CSSProperties = { margin: "0 0 10px", fontSize: 16, fontWeight: 700 }

function Kpi({ label, value, hint }: { label: string; value: number | string; hint?: string }) {
  return (
    <div style={card}>
      <div style={{ fontSize: 13, color: "var(--ink-2)" }}>{label}</div>
      <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: "-.02em", marginTop: 4 }}>{value}</div>
      {hint && <div style={{ fontSize: 12, color: "var(--ink-3)", marginTop: 2 }}>{hint}</div>}
    </div>
  )
}

function Legend({ items }: { items: Array<{ label: string; color: string }> }) {
  return (
    <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 10, fontSize: 13, color: "var(--ink-2)" }}>
      {items.map((item) => (
        <span key={item.label} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span aria-hidden="true" style={{ width: 10, height: 10, borderRadius: 3, background: item.color }} />
          {item.label}
        </span>
      ))}
    </div>
  )
}

interface Series {
  label: string
  color: string
  value: (day: DailyStats) => number
}

/** One bar per day. "overlay" draws each series over the previous one
 *  (visitors are a subset of page views); "stack" piles them up. Hovering a
 *  bar shows the exact figures. */
function BarChart({ days, series, mode }: { days: DailyStats[]; series: Series[]; mode: "overlay" | "stack" }) {
  const width = 720
  const height = 180
  const bottom = 22
  const left = 30
  const plotHeight = height - bottom - 6
  const slot = (width - left) / Math.max(days.length, 1)
  const totals = days.map((d) => (mode === "stack" ? sum(series.map((s) => s.value(d))) : Math.max(...series.map((s) => s.value(d)))))
  const max = Math.max(1, ...totals)
  const scale = (v: number) => (v / max) * plotHeight
  const labelEvery = Math.ceil(days.length / 10)

  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Graphique par jour" style={{ width: "100%", height: "auto", display: "block" }}>
      <text x={0} y={12} fontSize={11} fill="var(--ink-3)">
        {max}
      </text>
      <line x1={left} x2={width} y1={height - bottom} y2={height - bottom} stroke="var(--stroke-2)" />
      {days.map((d, i) => {
        const x = left + i * slot + slot * 0.15
        const barWidth = slot * 0.7
        const tooltip = `${d.day} · ${series.map((s) => `${s.label} : ${s.value(d)}`).join(" · ")}`
        let stacked = 0
        return (
          <g key={d.day}>
            <title>{tooltip}</title>
            <rect x={left + i * slot} y={0} width={slot} height={height - bottom} fill="transparent" />
            {series.map((s, si) => {
              const value = s.value(d)
              const h = scale(value)
              const y = height - bottom - (mode === "stack" ? scale(stacked) + h : h)
              if (mode === "stack") stacked += value
              const inset = mode === "overlay" ? barWidth * 0.2 * si : 0
              return value > 0 ? (
                <rect key={s.label} x={x + inset} y={y} width={barWidth - 2 * inset} height={h} rx={2} fill={s.color} />
              ) : null
            })}
            {i % labelEvery === 0 && (
              <text x={left + i * slot + slot / 2} y={height - 6} fontSize={10} textAnchor="middle" fill="var(--ink-3)">
                {shortDay(d.day)}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}

function Ranking({
  title,
  entries,
  format = (key: string) => key,
}: {
  title: string
  entries: Record<string, number>
  format?: (key: string) => string
}) {
  const rows = Object.entries(entries)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
  const max = rows[0]?.[1] ?? 1
  return (
    <section style={card}>
      <h2 style={sectionTitle}>{title}</h2>
      {rows.length === 0 ? (
        <p style={{ margin: 0, fontSize: 14, color: "var(--ink-2)" }}>Pas encore de données.</p>
      ) : (
        <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 8 }}>
          {rows.map(([key, count]) => (
            <li key={key} style={{ fontSize: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                <span style={{ overflowWrap: "anywhere" }}>{format(key)}</span>
                <span style={{ fontFamily: "var(--mono)", color: "var(--ink-2)" }}>{count}</span>
              </div>
              <div style={{ height: 4, borderRadius: 999, background: "var(--stroke)", marginTop: 4 }}>
                <div style={{ width: `${(100 * count) / max}%`, height: "100%", borderRadius: 999, background: "var(--ac)" }} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
