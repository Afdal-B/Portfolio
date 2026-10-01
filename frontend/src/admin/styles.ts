import type { CSSProperties } from "react"

/** Styles shared by the admin panels. */

export const card: CSSProperties = {
  padding: 18,
  borderRadius: 18,
  border: "1px solid var(--stroke-2)",
  background: "var(--panel)",
}

export const primaryBtn: CSSProperties = {
  padding: "11px 18px",
  borderRadius: 12,
  border: "1px solid var(--ac-line)",
  background: "var(--ac)",
  color: "var(--on-ac)",
  fontFamily: "inherit",
  fontWeight: 600,
  fontSize: 14,
  cursor: "pointer",
}

export const secondaryBtn: CSSProperties = {
  padding: "9px 14px",
  borderRadius: 12,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass-2)",
  color: "var(--ink)",
  fontFamily: "inherit",
  fontSize: 14,
  cursor: "pointer",
}
