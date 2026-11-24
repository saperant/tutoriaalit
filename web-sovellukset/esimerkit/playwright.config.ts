import { defineConfig, devices } from "@playwright/test";

// @alku asetukset
// Päästä päähän -testit ajetaan tuotantokäännöstä vastaan
// (npm run build && npm run e2e). Rajapinta mokataan testeissä.
export default defineConfig({
  testDir: "e2e",
  forbidOnly: true,                       // test.only ei pääse läpi
  reporter: [["line"]],
  use: {
    baseURL: "http://127.0.0.1:4173",
    locale: "fi-FI",
    trace: "off",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npx vite preview --port 4173 --strictPort --host 127.0.0.1",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: false,
  },
});
// @loppu asetukset
