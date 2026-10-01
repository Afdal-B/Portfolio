import { StrictMode, Suspense, lazy } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AppStateProvider } from './context/AppStateContext'

// The admin page is left out of production builds entirely (no route, no
// code in the public bundle) unless VITE_ENABLE_ADMIN=true at build time.
// Both values are replaced at build time, so the import below is dropped.
const adminEnabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_ADMIN === 'true'
const AdminApp = adminEnabled ? lazy(() => import('./admin/AdminApp').then((m) => ({ default: m.AdminApp }))) : null

// Two pages only, so a path check beats pulling in a router.
const isAdmin = AdminApp !== null && window.location.pathname.replace(/\/+$/, '') === '/admin'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {isAdmin && AdminApp ? (
      <Suspense fallback={null}>
        <AdminApp />
      </Suspense>
    ) : (
      <AppStateProvider>
        <App />
      </AppStateProvider>
    )}
  </StrictMode>,
)
