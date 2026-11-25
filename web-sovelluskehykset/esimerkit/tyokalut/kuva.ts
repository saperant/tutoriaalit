// Ottaa tekstin kuvituskuvan valmiista sovelluksesta (make kuvat).
// Kaikki toteutukset näyttävät samalta, joten kuva otetaan yhdestä.
import { chromium } from "@playwright/test";
import { join } from "node:path";
import kaynnista from "../e2e/palvelin.ts";

const sulje = await kaynnista();
const selain = await chromium.launch();
const sivu = await selain.newPage({
  viewport: { width: 640, height: 430 }, deviceScaleFactor: 2,
});
await sivu.goto(`${process.env.SOVELLUKSET}/svelte/`);
await sivu.getByRole("textbox", { name: "Tehtävä" }).fill("ti");
await sivu.getByRole("button", { name: "Lisää" }).click();
await sivu.getByRole("textbox", { name: "Tehtävä" }).fill("Tilaa kahvit");
await sivu.screenshot({
  path: join(import.meta.dirname, "..", "..", "kuvat", "sovellus.png"),
});
await selain.close();
await sulje();
