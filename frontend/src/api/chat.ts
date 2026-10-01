import { apiPost } from "./client"
import type { ChatResponse, Lang } from "../types/chat"

export function postChat(message: string, lang: Lang): Promise<ChatResponse> {
  return apiPost<ChatResponse>("/chat", { message, lang })
}
