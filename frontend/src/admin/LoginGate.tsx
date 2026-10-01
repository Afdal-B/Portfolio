import { useState, type FormEvent } from "react"

export function LoginGate({ onSubmit, error }: { onSubmit: (password: string) => void; error: string | null }) {
  const [password, setPassword] = useState("")

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (password.trim()) onSubmit(password.trim())
  }

  return (
    <div
      style={{
        minHeight: "100dvh",
        background: "var(--page)",
        color: "var(--ink)",
        display: "grid",
        placeItems: "center",
        padding: 20,
      }}
    >
      <form
        onSubmit={submit}
        style={{
          width: "min(380px, 100%)",
          padding: 24,
          borderRadius: 20,
          border: "1px solid var(--stroke-2)",
          background: "var(--panel)",
          boxShadow: "var(--shadow)",
        }}
      >
        <h1 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 6px" }}>Administration</h1>
        <p style={{ fontSize: 13.5, color: "var(--ink-2)", margin: "0 0 18px" }}>
          Mot de passe requis pour modifier les projets.
        </p>

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mot de passe"
          aria-label="Mot de passe administrateur"
          autoFocus
          style={{
            width: "100%",
            padding: "11px 14px",
            borderRadius: 12,
            border: "1px solid var(--stroke-2)",
            background: "var(--glass-2)",
            color: "var(--ink)",
            fontFamily: "inherit",
            fontSize: 15,
            outline: "none",
          }}
        />

        {error && <p style={{ color: "rgb(220,120,120)", fontSize: 13, margin: "12px 0 0" }}>{error}</p>}

        <button
          type="submit"
          style={{
            width: "100%",
            marginTop: 16,
            padding: "11px 18px",
            borderRadius: 12,
            border: "1px solid var(--ac-line)",
            background: "var(--ac)",
            color: "var(--on-ac)",
            fontFamily: "inherit",
            fontWeight: 600,
            fontSize: 13.5,
            cursor: "pointer",
          }}
        >
          Se connecter
        </button>
      </form>
    </div>
  )
}
