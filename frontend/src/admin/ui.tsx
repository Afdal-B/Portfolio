import type { ReactNode } from "react"

/** Small building blocks shared by the admin panels. */

export function Banner({ tone, children }: { tone: "ok" | "error" | "info"; children: ReactNode }) {
  const error = tone === "error"
  return (
    <div
      role="status"
      style={{
        marginBottom: 18,
        padding: "12px 14px",
        borderRadius: 14,
        fontSize: 14,
        lineHeight: 1.5,
        border: `1px solid ${error ? "rgba(220,80,80,.5)" : "var(--ac-line)"}`,
        background: error ? "rgba(220,80,80,.12)" : "var(--ac-soft)",
        color: "var(--ink)",
      }}
    >
      {children}
    </div>
  )
}
