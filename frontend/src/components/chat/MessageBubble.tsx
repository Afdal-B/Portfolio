import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { AskedItem, Engine } from "../../types/chat"
import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { TypingIndicator } from "./TypingIndicator"
import { TracePanel } from "./TracePanel"
import { PROSE_WIDTH } from "../../styles/layout"

// Answers are plain text: the page sections already show projects,
// experience and skills, so the assistant only ever writes.
const botBubble: React.CSSProperties = {
  maxWidth: "100%",
  padding: "18px 22px",
  borderRadius: 20,
  border: "1px solid var(--stroke-2)",
  background: "var(--glass)",
  boxShadow: "var(--shadow)",
  animation: "pfIn .26s ease-out",
}

const userBubble: React.CSSProperties = {
  maxWidth: "min(100%, 640px)",
  padding: "13px 20px",
  borderRadius: 20,
  border: "1px solid var(--ac-line)",
  background: "var(--ac-soft)",
  animation: "pfIn .2s ease-out",
}

const proseStyle: React.CSSProperties = {
  maxWidth: PROSE_WIDTH,
  fontSize: 17,
  lineHeight: 1.65,
  color: "var(--ink)",
  textWrap: "pretty",
}

function EngineBadge({ engine }: { engine: Engine }) {
  const { lang } = useAppState()
  const L = t(lang)
  const isRag = engine === "rag"
  return (
    <span
      style={{
        fontFamily: "var(--mono)",
        fontSize: 11,
        letterSpacing: ".06em",
        textTransform: "uppercase",
        padding: "2px 7px",
        borderRadius: 999,
        border: `1px solid ${isRag ? "var(--ac-line)" : "var(--stroke-2)"}`,
        background: isRag ? "var(--ac-soft)" : "transparent",
        color: isRag ? "var(--ac)" : "var(--ink-2)",
      }}
    >
      {isRag ? L.engineRag : L.engineScripted}
    </span>
  )
}

function BotHeader({ label, engine }: { label: string; engine?: Engine }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--ac)", boxShadow: "0 0 0 4px var(--ac-soft)" }} />
      <span style={{ fontFamily: "var(--mono)", fontSize: 12, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--ink-2)" }}>
        {label}
      </span>
      {engine && <EngineBadge engine={engine} />}
    </div>
  )
}

export function GreetingBubble({ text }: { text: string }) {
  const { lang } = useAppState()
  const L = t(lang)
  return (
    <div id="greeting" style={{ display: "flex", justifyContent: "flex-start" }}>
      <div style={botBubble}>
        <BotHeader label={L.bot} />
        <div style={proseStyle}>{text}</div>
      </div>
    </div>
  )
}

export function UserBubble({ index, text }: { index: number; text: string }) {
  return (
    <div id={`q-${index}`} style={{ display: "flex", justifyContent: "flex-end" }}>
      <div style={userBubble}>
        <div style={{ fontSize: 16, lineHeight: 1.5, color: "var(--ink)" }}>{text}</div>
      </div>
    </div>
  )
}

export function BotAnswerBubble({ index, item, pending }: { index: number; item: AskedItem; pending: boolean }) {
  const { lang } = useAppState()
  const L = t(lang)

  return (
    <div id={`a-${index}`} style={{ display: "flex", justifyContent: "flex-start" }}>
      <div style={botBubble}>
        <BotHeader label={L.bot} engine={pending ? undefined : item.engine} />
        {pending ? (
          <TypingIndicator />
        ) : (
          <>
            {/* Answers come as Markdown (lists, tables, bold). react-markdown
                renders no raw HTML, so model output can't inject markup. */}
            <div className="answer-md" style={proseStyle}>
              <Markdown remarkPlugins={[remarkGfm]}>{item.a}</Markdown>
            </div>
            {item.confidence != null && item.sources && (
              <TracePanel index={index} sources={item.sources} confidence={item.confidence} />
            )}
          </>
        )}
      </div>
    </div>
  )
}
