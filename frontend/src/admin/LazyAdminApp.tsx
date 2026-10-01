import { lazy } from "react"

/** The admin page, loaded only on /admin as a separate chunk: visitors of
 *  the site never download it. */
export const LazyAdminApp = lazy(() => import("./AdminApp").then((m) => ({ default: m.AdminApp })))
