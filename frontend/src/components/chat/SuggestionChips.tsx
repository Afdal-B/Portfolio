import { useAppState } from "../../context/AppStateContext"

export function SuggestionChips() {
  const { suggestions, ask } = useAppState()

  return (
    <div style={{ display: "flex", gap: 8, overflowX: "auto", padding: "0 2px 8px", scrollbarWidth: "none" }}>
      {suggestions.map((s) => (
        <button
          key={s.id}
          type="button"
          onClick={() => ask(s.label)}
          style={{
            flex: "none",
            whiteSpace: "nowrap",
            padding: "8px 13px",
            borderRadius: 999,
            border: "1px solid var(--stroke)",
            background: "var(--glass)",
            backdropFilter: "blur(18px)",
            fontFamily: "inherit",
            fontSize: 14,
            color: "var(--ink)",
            cursor: "pointer",
          }}
        >
          {s.label}
        </button>
      ))}
    </div>
  )
}
