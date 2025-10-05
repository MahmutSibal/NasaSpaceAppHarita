// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  css: [
    'leaflet/dist/leaflet.css'
  ],
  nitro: {
    compatibilityDate: '2025-09-15'
  },
  runtimeConfig: {
    public: {
      // Access via globalThis to avoid TS complaining about process types in config file context
      apiBase: (globalThis as any).process?.env?.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  }
})
