import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"

interface Props {
  index: number
  sources: string[]
  confidence: number
}

export function TracePanel({ index, sources, confidence }: Props) {
  const { lang, traces, toggleTrace } = useAppState()
  const L = t(lang)
  const open = !!traces[index]
  const filled = Math.round(confidence / 20)

  return (
    <>
      <div style={{ marginTop: 14 }}>
        <button
          type="button"
          onClick={() => toggleTrace(index)}
          style={{
            background: "none",
            border: 0,
            padding: 0,
            cursor: "pointer",
            fontFamily: "var(--mono)",
            fontSize: 12.5,
            color: "var(--ink-2)",
            textDecoration: "underline",
            textUnderlineOffset: 3,
          }}
        >
          {open ? L.traceHide : L.traceLabel}
        </button>
      </div>
      {open && (
        <div
          style={{
            marginTop: 12,
            padding: 14,
            borderRadius: 14,
            background: "var(--ac-soft)",
            border: "1px solid var(--ac-line)",
            animation: "pfFade .2s ease-out",
          }}
        >
          <div style={{ fontFamily: "var(--mono)", fontSize: 11.5, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--ink-2)", marginBottom: 8 }}>
            {L.traceSources}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 5, marginBottom: 12 }}>
            {sources.map((s, i) => (
              <span key={i} style={{ fontFamily: "var(--mono)", fontSize: 13, lineHeight: 1.5, color: "var(--ink)" }}>
                · {s}
              </span>
            ))}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontFamily: "var(--mono)", fontSize: 11.5, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--ink-2)" }}>
              {L.traceConfidence}
            </span>
            <span style={{ display: "flex", gap: 3 }}>
              {Array.from({ length: 5 }, (_, i) => (
                <span
                  key={i}
                  style={{
                    width: 16,
                    height: 4,
                    borderRadius: 999,
                    background: i < filled ? "var(--ac)" : "var(--stroke-2)",
                  }}
                />
              ))}
            </span>
            <span style={{ fontFamily: "var(--mono)", fontSize: 13, fontWeight: 500 }}>{confidence} %</span>
          </div>
        </div>
      )}
    </>
  )
}
