import type { AdminProject } from "../types/content"
import { ImageUploader } from "./ImageUploader"

type BilingualField = "meta" | "title" | "summary" | "result" | "problem" | "method" | "metrics"

const FIELDS: Array<{ key: BilingualField; label: string; multiline?: boolean }> = [
  { key: "title", label: "Titre" },
  { key: "meta", label: "Domaine (ex: NLP · Classification)" },
  { key: "summary", label: "Résumé de la carte (2 phrases ; vide = le résultat)", multiline: true },
  { key: "problem", label: "Problème", multiline: true },
  { key: "method", label: "Méthode", multiline: true },
  { key: "result", label: "Résultat", multiline: true },
  { key: "metrics", label: "Métriques", multiline: true },
]

export function ProjectEditor({
  project,
  index,
  total,
  token,
  onChange,
  onRemove,
  onMove,
  onError,
}: {
  project: AdminProject
  index: number
  total: number
  token: string
  onChange: (next: AdminProject) => void
  onRemove: () => void
  onMove: (direction: -1 | 1) => void
  onError: (message: string) => void
}) {
  const setBilingual = (field: BilingualField, lang: "fr" | "en", value: string) =>
    onChange({ ...project, [field]: { ...project[field], [lang]: value } })

  return (
    <section
      style={{
        padding: 18,
        borderRadius: 18,
        border: "1px solid var(--stroke-2)",
        background: "var(--panel)",
        boxShadow: "var(--shadow)",
      }}
    >
      <header style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        <strong style={{ fontSize: 14.5, marginRight: "auto" }}>
          {project.title.fr || project.title.en || "Nouveau projet"}
          {project.id && (
            <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--ink-2)", marginLeft: 8 }}>
              {project.id}
            </span>
          )}
        </strong>
        <button type="button" onClick={() => onMove(-1)} disabled={index === 0} style={iconBtn} aria-label="Monter">
          ↑
        </button>
        <button
          type="button"
          onClick={() => onMove(1)}
          disabled={index === total - 1}
          style={iconBtn}
          aria-label="Descendre"
        >
          ↓
        </button>
        <button type="button" onClick={onRemove} style={{ ...iconBtn, color: "rgb(220,120,120)" }} aria-label="Supprimer">
          ✕
        </button>
      </header>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {FIELDS.map(({ key, label, multiline }) => (
          <div key={key}>
            <label style={labelStyle}>{label}</label>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 8 }}>
              {(["fr", "en"] as const).map((lang) => (
                <Field
                  key={lang}
                  lang={lang}
                  multiline={multiline}
                  value={project[key]?.[lang] ?? ""}
                  onChange={(value) => setBilingual(key, lang, value)}
                />
              ))}
            </div>
          </div>
        ))}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 8 }}>
          <div>
            <label style={labelStyle}>Stack (commun FR/EN ; les 3 premiers vont sur la carte)</label>
            <input
              value={project.stack}
              onChange={(e) => onChange({ ...project, stack: e.target.value })}
              placeholder="Python · PyTorch · MLflow"
              style={inputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>Lien de la démo</label>
            <input
              value={project.url}
              onChange={(e) => onChange({ ...project, url: e.target.value })}
              placeholder="#"
              style={inputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>Lien du code ou du modèle (optionnel)</label>
            <input
              value={project.code_url}
              onChange={(e) => onChange({ ...project, code_url: e.target.value })}
              placeholder="https://github.com/…"
              style={inputStyle}
            />
          </div>
        </div>

        <ImageUploader
          token={token}
          imageUrl={project.image_url}
          screenshots={project.screenshots}
          onChange={(patch) => onChange({ ...project, ...patch })}
          onError={onError}
        />
      </div>
    </section>
  )
}

function Field({
  lang,
  value,
  multiline,
  onChange,
}: {
  lang: "fr" | "en"
  value: string
  multiline?: boolean
  onChange: (value: string) => void
}) {
  const shared = { ...inputStyle, paddingLeft: 38 }
  return (
    <div style={{ position: "relative" }}>
      <span
        aria-hidden="true"
        style={{
          position: "absolute",
          left: 12,
          top: 11,
          fontFamily: "var(--mono)",
          fontSize: 10,
          textTransform: "uppercase",
          color: "var(--ink-3)",
        }}
      >
        {lang}
      </span>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          aria-label={lang}
          style={{ ...shared, resize: "vertical" }}
        />
      ) : (
        <input value={value} onChange={(e) => onChange(e.target.value)} aria-label={lang} style={shared} />
      )}
    </div>
  )
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 12,
  fontWeight: 500,
  color: "var(--ink-2)",
  marginBottom: 5,
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "9px 12px",
  borderRadius: 10,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass-2)",
  color: "var(--ink)",
  fontFamily: "inherit",
  fontSize: 13.5,
  lineHeight: 1.5,
  outline: "none",
}

const iconBtn: React.CSSProperties = {
  width: 30,
  height: 30,
  display: "grid",
  placeItems: "center",
  borderRadius: 9,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass-2)",
  color: "var(--ink)",
  cursor: "pointer",
  fontSize: 13,
}
