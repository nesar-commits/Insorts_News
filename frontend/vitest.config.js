import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Deliberately separate from vite.config.js: the PWA plugin there runs a
// real injectManifest service-worker build on startup, which is pointless
// overhead for unit tests and not something we want tests coupled to.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    globals: true,
  },
})
