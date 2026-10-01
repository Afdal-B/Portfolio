const dot: React.CSSProperties = {
  width: 7,
  height: 7,
  borderRadius: "50%",
  background: "var(--ink-2)",
  animation: "pfDot 1.1s ease-in-out infinite",
}

export function TypingIndicator() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 0 2px" }}>
      <span style={dot} />
      <span style={{ ...dot, animationDelay: ".18s" }} />
      <span style={{ ...dot, animationDelay: ".36s" }} />
    </div>
  )
}
