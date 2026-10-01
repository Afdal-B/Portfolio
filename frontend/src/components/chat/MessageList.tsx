import { useEffect, useRef } from "react"
import { useAppState } from "../../context/AppStateContext"
import { t } from "../../i18n/copy"
import { useAutoScroll } from "../../hooks/useAutoScroll"
import { GreetingBubble, UserBubble, BotAnswerBubble } from "./MessageBubble"

export function MessageList() {
  const { lang, asked, pending } = useAppState()
  const L = t(lang)
  const containerRef = useRef<HTMLDivElement>(null)
  const scrollToQuestion = useAutoScroll(containerRef)

  useEffect(() => {
    scrollToQuestion(asked.length - 1)
  }, [asked.length, pending, scrollToQuestion])

  return (
    <section
      id="chatScroll"
      ref={containerRef}
      style={{
        flex: 1,
        minHeight: 0,
        overflowY: "auto",
        overflowX: "hidden",
        padding: "20px 20px 24px",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 18,
        }}
      >
        <GreetingBubble text={L.greeting} />
        {asked.map((item, i) => (
          <div key={i} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <UserBubble index={i} text={item.q} />
            <BotAnswerBubble index={i} item={item} pending={pending && i === asked.length - 1} />
          </div>
        ))}
      </div>
    </section>
  )
}
