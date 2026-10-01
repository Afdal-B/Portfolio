/** Marks this browser as the site owner's, so their own visits and
 *  questions stay out of the statistics. Set from the admin page; kept in
 *  localStorage, which can be unavailable (private mode): then the browser
 *  simply counts as a visitor. */

const OWNER_KEY = "pf-owner"

export function isOwner(): boolean {
  try {
    return localStorage.getItem(OWNER_KEY) === "1"
  } catch {
    return false
  }
}

export function setOwner(owner: boolean): void {
  try {
    if (owner) localStorage.setItem(OWNER_KEY, "1")
    else localStorage.removeItem(OWNER_KEY)
  } catch {
    /* storage unavailable: nothing to remember */
  }
}

/** Header the backend reads to skip recording the request. */
export function ownerHeaders(): Record<string, string> {
  return isOwner() ? { "x-pf-owner": "1" } : {}
}
