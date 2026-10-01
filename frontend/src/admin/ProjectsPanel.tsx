import { useEffect, useState } from "react"
import { AdminAuthError, getAdminProjects, saveAdminProjects } from "../api/admin"
import type { AdminProject } from "../types/content"
import { ProjectEditor } from "./ProjectEditor"
import { Banner } from "./ui"
import { primaryBtn, secondaryBtn } from "./styles"

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

export function ProjectsPanel({ token, onAuthError }: { token: string; onAuthError: () => void }) {
  const [projects, setProjects] = useState<AdminProject[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
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
        if (err instanceof AdminAuthError) onAuthError()
      })
    return () => {
      cancelled = true
    }
  }, [token, onAuthError])

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
      setStatus(
        `Enregistré : ${saved.length} projet(s). Pensez à lancer \`make embeddings\` avant de pousser, pour que l'assistant les connaisse en ligne.`,
      )
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur inconnue")
      if (err instanceof AdminAuthError) onAuthError()
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
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
    </>
  )
}
