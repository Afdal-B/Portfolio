import { isOwner, ownerHeaders } from "./owner"

/** One anonymous visit beacon per page load: no cookie, and the backend
 *  keeps no IP address. Skipped in development and for the site owner. */
export function recordVisit(): void {
  if (import.meta.env.DEV || isOwner()) return
  fetch("/api/analytics/visit", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...ownerHeaders() },
    body: JSON.stringify({ referrer: document.referrer || null }),
    keepalive: true,
  }).catch(() => {
    /* statistics are best effort */
  })
}
