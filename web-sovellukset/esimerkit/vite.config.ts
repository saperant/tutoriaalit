import { defineConfig } from "vitest/config";
import { TURVAOTSAKKEET } from "./turvaotsakkeet.ts";

// Yksi asetustiedosto sekä Vitelle (kehityspalvelin ja tuotantokäännös)
// että Vitestille (yksikkö- ja komponenttitestit).
export default defineConfig({
  // Kehityksessä /api ohjataan paikalliselle palvelimelle
  // (node palvelin/api.ts), jolloin selain näkee yhden alkuperän eikä
  // CORS-asetuksia tarvita.
  server: { proxy: { "/api": "http://127.0.0.1:3001" } },
  preview: {
    proxy: { "/api": "http://127.0.0.1:3001" },
    headers: TURVAOTSAKKEET,
  },
  build: { outDir: "dist", sourcemap: true },
  test: {
    environment: "happy-dom",
    include: ["src/**/*.test.{ts,tsx}"],
    restoreMocks: true,
    setupFiles: ["src/testiasetukset.ts"],
  },
});
