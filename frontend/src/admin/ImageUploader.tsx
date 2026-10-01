import { useRef, useState, type ChangeEvent } from "react"
import { uploadImage } from "../api/admin"

const MAX_SCREENSHOTS = 3

export function ImageUploader({
  token,
  imageUrl,
  screenshots,
  onChange,
  onError,
}: {
  token: string
  imageUrl: string
  screenshots: string[]
  onChange: (next: { image_url?: string; screenshots?: string[] }) => void
  onError: (message: string) => void
}) {
  const [busy, setBusy] = useState<"main" | "shot" | null>(null)
  const mainInput = useRef<HTMLInputElement>(null)
  const shotInput = useRef<HTMLInputElement>(null)

  const upload = async (event: ChangeEvent<HTMLInputElement>, target: "main" | "shot") => {
    const files = Array.from(event.target.files ?? [])
    event.target.value = "" // let the same file be picked again after a removal
    if (files.length === 0) return

    setBusy(target)
    try {
      const urls = await Promise.all(files.map((file) => uploadImage(token, file)))
      if (target === "main") {
        onChange({ image_url: urls[0] })
      } else {
        onChange({ screenshots: [...screenshots, ...urls].slice(0, MAX_SCREENSHOTS) })
      }
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : "Échec de l'upload")
    } finally {
      setBusy(null)
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div>
        <label style={labelStyle}>Image principale (carte + visuel de la modale)</label>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          {imageUrl ? (
            <div style={{ position: "relative" }}>
              <img src={imageUrl} alt="" style={thumbStyle} />
              <button
                type="button"
                onClick={() => onChange({ image_url: "" })}
                aria-label="Retirer l'image principale"
                style={removeBadge}
              >
                ✕
              </button>
            </div>
          ) : (
            <span style={{ ...thumbStyle, ...emptyThumb }}>Placeholder</span>
          )}
          <button type="button" onClick={() => mainInput.current?.click()} disabled={busy !== null} style={uploadBtn}>
            {busy === "main" ? "Envoi…" : imageUrl ? "Remplacer" : "Choisir une image"}
          </button>
          <input
            ref={mainInput}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => upload(e, "main")}
            style={{ display: "none" }}
          />
        </div>
      </div>

      <div>
        <label style={labelStyle}>Aperçus dans la modale (jusqu'à {MAX_SCREENSHOTS})</label>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          {screenshots.map((url, i) => (
            <div key={url} style={{ position: "relative" }}>
              <img src={url} alt="" style={thumbStyle} />
              <button
                type="button"
                onClick={() => onChange({ screenshots: screenshots.filter((_, index) => index !== i) })}
                aria-label={`Retirer l'aperçu ${i + 1}`}
                style={removeBadge}
              >
                ✕
              </button>
            </div>
          ))}
          {screenshots.length < MAX_SCREENSHOTS && (
            <button type="button" onClick={() => shotInput.current?.click()} disabled={busy !== null} style={uploadBtn}>
              {busy === "shot" ? "Envoi…" : "+ Ajouter"}
            </button>
          )}
          <input
            ref={shotInput}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            onChange={(e) => upload(e, "shot")}
            style={{ display: "none" }}
          />
        </div>
        <p style={{ fontSize: 11.5, color: "var(--ink-3)", margin: "6px 0 0" }}>
          JPEG, PNG ou WebP · 4 Mo max. Les images sont automatiquement redimensionnées (1600 px max) et
          converties en WebP. Sans image, un placeholder est affiché.
        </p>
      </div>
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

const thumbStyle: React.CSSProperties = {
  display: "block",
  width: 104,
  height: 59,
  objectFit: "cover",
  borderRadius: 8,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass-2)",
}

const emptyThumb: React.CSSProperties = {
  display: "grid",
  placeItems: "center",
  fontFamily: "var(--mono)",
  fontSize: 10,
  color: "var(--ink-3)",
}

const uploadBtn: React.CSSProperties = {
  padding: "8px 13px",
  borderRadius: 10,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass-2)",
  color: "var(--ink)",
  fontFamily: "inherit",
  fontSize: 12.5,
  cursor: "pointer",
}

const removeBadge: React.CSSProperties = {
  position: "absolute",
  top: -6,
  right: -6,
  width: 20,
  height: 20,
  display: "grid",
  placeItems: "center",
  borderRadius: "50%",
  border: "1px solid var(--stroke-2)",
  background: "var(--panel)",
  color: "rgb(220,120,120)",
  fontSize: 10,
  cursor: "pointer",
}
