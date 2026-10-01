/** "Model" for a Hugging Face model page, "Code" for anything else. */
export function codeLinkLabel(url: string, L: { code: string; model: string }): string {
  try {
    const u = new URL(url)
    return u.hostname.endsWith("huggingface.co") && !u.pathname.startsWith("/spaces/") ? L.model : L.code
  } catch {
    return L.code
  }
}
