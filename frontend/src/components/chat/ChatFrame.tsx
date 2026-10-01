import { MessageList } from "./MessageList"
import { Composer } from "./Composer"

/** The conversation panel. Fixed height so the page around it stays put:
 *  messages scroll inside it, never the page. The height leaves room for
 *  the sticky header and the section's heading, so the whole assistant fits
 *  on one screen once the visitor lands on it. */
export function ChatFrame() {
  return (
    <div
      style={{
        height: "clamp(340px, calc(100dvh - 310px), 600px)",
        display: "flex",
        flexDirection: "column",
        border: "1px solid var(--stroke-2)",
        borderRadius: 18,
        background: "var(--page)",
        overflow: "hidden",
      }}
    >
      <MessageList />
      <Composer />
    </div>
  )
}
