import { defineConfig, devices } from "@playwright/test";

// @alku asetukset
// Sama testisarja (e2e/sovellus.spec.ts) ajetaan jokaista toteutusta
// vasten: projektin nimi on toteutuksen hakemisto dist/-hakemistossa.
export const TOTEUTUKSET = ["paljas", "react", "vue", "angular", "svelte"];

export default defineConfig({
  testDir: "e2e",
  globalSetup: "./e2e/palvelin.ts",
  forbidOnly: true,
  reporter: [["line"]],
  use: { ...devices["Desktop Chrome"], locale: "fi-FI", trace: "off" },
  projects: TOTEUTUKSET.map((name) => ({ name })),
});
// @loppu asetukset
