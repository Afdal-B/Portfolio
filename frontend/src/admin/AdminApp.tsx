import { useCallback, useEffect, useState } from "react"
import { AdminAuthError, getCapabilities } from "../api/admin"
import { setOwner } from "../lib/owner"
import type { AdminCapabilities } from "../types/stats"
import { LoginGate } from "./LoginGate"
import { ProjectsPanel } from "./ProjectsPanel"
import { StatsPanel } from "./StatsPanel"
import { secondaryBtn } from "./styles"

const TOKEN_KEY = "portfolio-admin-token"

type Tab = "stats" | "projects"

function readStoredToken(): string {
  try {
    return sessionStorage.getItem(TOKEN_KEY) ?? ""
  } catch {
    return ""
  }
}

export function AdminApp() {
  const [token, setToken] = useState(readStoredToken)
  const [capabilities, setCapabilities] = useState<AdminCapabilities | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>("stats")

  useEffect(() => {
    document.documentElement.setAttribute("data-pf", "dark")
  }, [])

  const signOut = useCallback(() => {
    try {
      sessionStorage.removeItem(TOKEN_KEY)
    } catch {
      /* sessionStorage can be unavailable (private mode): the in-memory token still clears */
    }
    setToken("")
    setCapabilities(null)
  }, [])

  useEffect(() => {
    if (!token) return
    let cancelled = false
    getCapabilities(token)
      .then((loaded) => {
        if (cancelled) return
        setCapabilities(loaded)
        setError(null)
        // Whoever signs in here is the owner: keep this browser out of the
        // statistics from now on (it can be undone from the dashboard).
        setOwner(true)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "Erreur inconnue")
        if (err instanceof AdminAuthError) signOut()
      })
    return () => {
      cancelled = true
    }
  }, [token, signOut])

  const signIn = (password: string) => {
    try {
      sessionStorage.setItem(TOKEN_KEY, password)
    } catch {
      /* fall back to keeping it in memory only for this page view */
    }
    setError(null)
    setToken(password)
  }

  if (!token) return <LoginGate onSubmit={signIn} error={error} />

  const tabs: Array<{ id: Tab; label: string }> = [
    { id: "stats", label: "Statistiques" },
    ...(capabilities?.projects_editable ? [{ id: "projects" as const, label: "Projets" }] : []),
  ]

  return (
    <div style={{ minHeight: "100dvh", background: "var(--page)", color: "var(--ink)", padding: "28px 20px 60px" }}>
      <div style={{ maxWidth: 1000, margin: "0 auto" }}>
        <header style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", marginBottom: 22 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.02em", margin: 0 }}>Administration</h1>
          {tabs.length > 1 && (
            <nav aria-label="Sections" style={{ display: "flex", gap: 6 }}>
              {tabs.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTab(t.id)}
                  aria-pressed={tab === t.id}
                  style={{
                    ...secondaryBtn,
                    ...(tab === t.id ? { background: "var(--ac-soft)", borderColor: "var(--ac-line)", color: "var(--ac)" } : {}),
                  }}
                >
                  {t.label}
                </button>
              ))}
            </nav>
          )}
          <span style={{ marginLeft: "auto" }} />
          <a href="/" style={{ fontSize: 14 }}>
            ← Retour au site
          </a>
          <button type="button" onClick={signOut} style={secondaryBtn}>
            Se déconnecter
          </button>
        </header>

        {!capabilities ? (
          <p style={{ color: "var(--ink-2)" }}>{error ?? "Chargement…"}</p>
        ) : tab === "projects" && capabilities.projects_editable ? (
          <ProjectsPanel token={token} onAuthError={signOut} />
        ) : (
          <StatsPanel token={token} onAuthError={signOut} />
        )}
      </div>
    </div>
  )
}
