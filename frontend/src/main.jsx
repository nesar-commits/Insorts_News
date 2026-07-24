import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import App from './App.jsx'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'

// Prevent the browser from restoring the previous scroll offset on reload —
// with infinite-scroll content, restoring an old pixel offset onto a freshly
// (and much shorter) loaded page makes the load-more sentinel appear
// in-view immediately, triggering a runaway auto-fetch cascade instead of
// simply starting at the top like a fresh page load should.
if ('scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual'
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      refetchOnWindowFocus: false,
      // The Render free-tier backend spins down after ~15 min idle; the
      // request that wakes it can take 20-50s to actually respond. A single
      // quick retry (the old default) gives up before that finishes — retry
      // longer so a cold start self-heals instead of showing an error.
      retry: 5,
      retryDelay: (attemptIndex) => Math.min(3000 * (attemptIndex + 1), 15000),
    },
  },
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
)
