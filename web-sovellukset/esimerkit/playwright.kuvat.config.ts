import { defineConfig } from "@playwright/test";
import asetukset from "./playwright.config.ts";

// Tutoriaalin kuvakaappaukset (make kuvat). Sama selain ja sama
// tuotantokäännös kuin päästä päähän -testeissä, mutta oma hakemisto,
// jotta kuvitus ei kuulu testiajoon.
export default defineConfig({
  ...asetukset,
  testDir: "kuvitus",
  workers: 1,
  use: {
    ...asetukset.use,
    // Selaimen oma kieli: päivämäärä- ja aikakentät suomalaisittain.
    launchOptions: { args: ["--lang=fi-FI"],
                     env: { ...process.env, LANGUAGE: "fi_FI" } },
  },
});
