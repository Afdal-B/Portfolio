import { useCallback, useEffect, useState } from "react"
import { AdminAuthError, getAdminProjects, saveAdminProjects } from "../api/admin"
import type { AdminProject } from "../types/content"
import { ProjectEditor } from "./ProjectEditor"
import { LoginGate } from "./LoginGate"

const TOKEN_KEY = "portfolio-admin-token"

function emptyProject(): AdminProject {
  return {
    id: "",
    meta: { fr: "", en: "" },
    title: { fr: "", en: "" },
    result: { fr: "", en: "" },
    problem: { fr: "", en: "" },
    method: { fr: "", en: "" },
    stack: "",
    metrics: { fr: "", en: "" },
    url: "#",
    image_url: "",
    screenshots: [],
    image_seed: "",
    summary: { fr: "", en: "" },
    code_url: "",
  }
}

function readStoredToken(): string {
  try {
    return sessionStorage.getItem(TOKEN_KEY) ?? ""
  } catch {
    return ""
  }
}

export function AdminApp() {
  const [token, setToken] = useState(readStoredToken)
  const [projects, setProjects] = useState<AdminProject[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    document.documentElement.setAttribute("data-pf", "dark")
  }, [])

  const signOut = useCallback(() => {
    try {
      sessionStorage.removeItem(TOKEN_KEY)
    } catch {
      /* sessionStorage can be unavailable (private mode) — the in-memory token still clears */
    }
    setToken("")
    setProjects(null)
  }, [])

  useEffect(() => {
    if (!token) return
    let cancelled = false
    getAdminProjects(token)
      .then((loaded) => {
        if (cancelled) return
        setProjects(loaded)
        setError(null)
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

  const update = (index: number, next: AdminProject) => {
    setProjects((prev) => prev && prev.map((p, i) => (i === index ? next : p)))
    setStatus(null)
  }

  const remove = (index: number) => {
    setProjects((prev) => prev && prev.filter((_, i) => i !== index))
    setStatus(null)
  }

  const move = (index: number, direction: -1 | 1) => {
    setProjects((prev) => {
      if (!prev) return prev
      const target = index + direction
      if (target < 0 || target >= prev.length) return prev
      const next = [...prev]
      ;[next[index], next[target]] = [next[target], next[index]]
      return next
    })
    setStatus(null)
  }

  const add = () => {
    setProjects((prev) => [...(prev ?? []), emptyProject()])
    setStatus(null)
  }

  const save = async () => {
    if (!projects) return
    setSaving(true)
    setError(null)
    try {
      const saved = await saveAdminProjects(token, projects)
      setProjects(saved)
      setStatus(`Enregistré : ${saved.length} projet(s). Le chatbot est à jour.`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur inconnue")
      if (err instanceof AdminAuthError) signOut()
    } finally {
      setSaving(false)
    }
  }

  if (!token) return <LoginGate onSubmit={signIn} error={error} />

  return (
    <div style={{ minHeight: "100dvh", background: "var(--page)", color: "var(--ink)", padding: "28px 20px 60px" }}>
      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        <header style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", marginBottom: 22 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.02em", margin: 0, marginRight: "auto" }}>
            Administration : projets
          </h1>
          <a href="/" style={{ fontSize: 13 }}>
            ← Retour au site
          </a>
          <button type="button" onClick={signOut} style={secondaryBtn}>
            Se déconnecter
          </button>
        </header>

        {error && <Banner tone="error">{error}</Banner>}
        {status && <Banner tone="ok">{status}</Banner>}

        {!projects ? (
          <p style={{ color: "var(--ink-2)" }}>Chargement…</p>
        ) : (
          <>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {projects.map((project, index) => (
                <ProjectEditor
                  key={project.id || `new-${index}`}
                  project={project}
                  index={index}
                  total={projects.length}
                  token={token}
                  onChange={(next) => update(index, next)}
                  onRemove={() => remove(index)}
                  onMove={(direction) => move(index, direction)}
                  onError={setError}
                />
              ))}
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 20, flexWrap: "wrap" }}>
              <button type="button" onClick={add} style={secondaryBtn}>
                + Ajouter un projet
              </button>
              <button type="button" onClick={save} disabled={saving} style={{ ...primaryBtn, opacity: saving ? 0.6 : 1 }}>
                {saving ? "Enregistrement…" : "Enregistrer"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function Banner({ tone, children }: { tone: "ok" | "error"; children: React.ReactNode }) {
  return (
    <div
      role="status"
      style={{
        marginBottom: 18,
        padding: "12px 14px",
        borderRadius: 14,
        fontSize: 13.5,
        border: `1px solid ${tone === "ok" ? "var(--ac-line)" : "rgba(220,80,80,.5)"}`,
        background: tone === "ok" ? "var(--ac-soft)" : "rgba(220,80,80,.12)",
        color: "var(--ink)",
      }}
    >
      {children}
    </div>
  )
}

const primaryBtn: React.CSSProperties = {
  padding: "11px 18px",
  borderRadius: 12,
  border: "1px solid var(--ac-line)",
  background: "var(--ac)",
  color: "var(--on-ac)",
  fontFamily: "inherit",
  fontWeight: 600,
  fontSize: 13.5,
  cursor: "pointer",
}

const secondaryBtn: React.CSSProperties = {
  padding: "9px 14px",
  borderRadius: 12,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass-2)",
  color: "var(--ink)",
  fontFamily: "inherit",
  fontSize: 13,
  cursor: "pointer",
}
