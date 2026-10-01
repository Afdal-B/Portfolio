import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AppStateProvider } from './context/AppStateContext'
import { recordVisit } from './lib/analytics'
import { LazyAdminApp } from './admin/LazyAdminApp'

// Two pages only, so a path check beats pulling in a router.
const isAdmin = window.location.pathname.replace(/\/+$/, '') === '/admin'

if (!isAdmin) recordVisit()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {isAdmin ? (
      <Suspense fallback={null}>
        <LazyAdminApp />
      </Suspense>
    ) : (
      <AppStateProvider>
        <App />
      </AppStateProvider>
    )}
  </StrictMode>,
)
