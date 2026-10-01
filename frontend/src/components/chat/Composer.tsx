import type { FormEvent } from "react"
import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { SuggestionChips } from "./SuggestionChips"

export function Composer() {
  const { lang, draft, setDraft, ask } = useAppState()
  const L = t(lang)

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    ask(draft)
  }

  return (
    <div style={{ flex: "none", borderTop: "1px solid var(--stroke-2)", padding: "12px 16px 16px", background: "var(--panel)" }}>
      <div>
        <SuggestionChips />
        <form
          onSubmit={onSubmit}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "7px 7px 7px 18px",
            borderRadius: 18,
            border: "1px solid var(--stroke-2)",
            background: "var(--chip)",
          }}
        >
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={L.inputPlaceholder}
            aria-label={L.inputPlaceholder}
            maxLength={500}
            style={{ flex: 1, minWidth: 0, border: 0, background: "transparent", fontFamily: "inherit", fontSize: 17, color: "var(--ink)", padding: "10px 0", outline: "none" }}
          />
          <button
            type="submit"
            aria-label={L.send}
            style={{
              width: 42,
              height: 42,
              flex: "none",
              display: "grid",
              placeItems: "center",
              borderRadius: 14,
              border: 0,
              background: "var(--ac)",
              color: "var(--on-ac)",
              cursor: "pointer",
              fontSize: 19,
              fontWeight: 700,
            }}
          >
            ↑
          </button>
        </form>
      </div>
    </div>
  )
}
