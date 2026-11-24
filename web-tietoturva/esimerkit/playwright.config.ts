import { defineConfig, devices } from "@playwright/test";

// Selaintestit käynnistävät tarvitsemansa palvelimet itse
// (e2e/*.spec.ts), joten webServer-asetusta ei tarvita.
export default defineConfig({
  testDir: "e2e",
  forbidOnly: true,
  reporter: [["line"]],
  use: { locale: "fi-FI", trace: "off" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
