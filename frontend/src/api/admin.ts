import type { AdminProject } from "../types/content"
import type { AdminCapabilities, Stats } from "../types/stats"

const BASE = "/api/admin"

class AdminAuthError extends Error {}

async function request<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...init?.headers, "Content-Type": "application/json", Authorization: `Bearer ${token}` },
  })
  if (res.status === 401) throw new AdminAuthError("Mot de passe incorrect")
  if (res.status === 404) throw new AdminAuthError("L'administration n'est pas activée sur ce serveur")
  if (res.status === 429) throw new AdminAuthError("Trop de tentatives, réessayez dans une heure")
  if (!res.ok) {
    const detail = await res.json().catch(() => null)
    throw new Error(detail?.detail ?? `${init?.method ?? "GET"} ${path} a échoué (${res.status})`)
  }
  return res.json() as Promise<T>
}

export function getCapabilities(token: string): Promise<AdminCapabilities> {
  return request<AdminCapabilities>("/capabilities", token)
}

export function getStats(token: string, days: number): Promise<Stats> {
  return request<Stats>(`/stats?days=${days}`, token)
}

export function getAdminProjects(token: string): Promise<AdminProject[]> {
  return request<AdminProject[]>("/projects", token)
}

export function saveAdminProjects(token: string, projects: AdminProject[]): Promise<AdminProject[]> {
  return request<AdminProject[]>("/projects", token, { method: "PUT", body: JSON.stringify(projects) })
}

export async function uploadImage(token: string, file: File): Promise<string> {
  const body = new FormData()
  body.append("file", file)
  // No Content-Type header here: the browser must set the multipart boundary.
  const res = await fetch(`${BASE}/uploads`, { method: "POST", body, headers: { Authorization: `Bearer ${token}` } })

  if (res.status === 401) throw new AdminAuthError("Mot de passe incorrect")
  if (!res.ok) {
    const detail = await res.json().catch(() => null)
    throw new Error(detail?.detail ?? `Échec de l'upload (${res.status})`)
  }
  const result = (await res.json()) as { url: string }
  return result.url
}

export { AdminAuthError }
