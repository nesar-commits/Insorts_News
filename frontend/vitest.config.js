import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Deliberately separate from vite.config.js: the PWA plugin there runs a
// real injectManifest service-worker build on startup, which is pointless
// overhead for unit tests and not something we want tests coupled to.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    // jsdom needs a real http(s) origin to install window.localStorage.
    environmentOptions: { jsdom: { url: 'http://localhost/' } },
    setupFiles: './src/test/setup.js',
    globals: true,
  },
  // NOTE: running vitest directly (not via `npm test`) on Node 22+ needs
  // NODE_OPTIONS=--no-experimental-webstorage — Node's own unconfigured
  // global `localStorage` shadows jsdom's, leaving window.localStorage
  // (and anything that reads/writes it: theme, auth cache, push category
  // preferences) silently undefined otherwise. See package.json's "test" script.
})
