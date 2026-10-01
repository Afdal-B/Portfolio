import { ownerHeaders } from "../lib/owner"

const BASE = "/api"

/** A non-2xx response, keeping the status so callers can tell a rate limit
 *  (429) from the server being down. */
export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

export async function apiGet<T>(path: string, params?: Record<string, string>): Promise<T> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : ""
  const res = await fetch(`${BASE}${path}${qs}`)
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
  return res.json() as Promise<T>
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...ownerHeaders() },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new ApiError(`POST ${path} failed: ${res.status}`, res.status)
  return res.json() as Promise<T>
}
