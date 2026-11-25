import { test, expect } from "@playwright/test";
import { kaynnista } from "../src/http.ts";
import { cdn, sivu } from "../src/03-xss/sri.ts";
import { taulu, tallenna } from "../src/taulu.ts";

const rivit: string[][] = [];

// @alku testi
for (const murrettu of [false, true]) {
  for (const sri of [false, true]) {
    test(`SRI ${sri ? "käytössä" : "ei käytössä"}, CDN ${
      murrettu ? "murrettu" : "kunnossa"}`, async ({ page }) => {
      const c = await kaynnista(cdn(murrettu), "127.0.0.2");
      const s = await kaynnista(sivu(c.url, sri));
      try {
        await page.goto(s.url);
        const arvo = await page.evaluate(() =>
          (window as { kirjasto?: string }).kirjasto ?? "ei ajettu");
        // Muutettu kirjasto ajetaan vain, jos tiivistettä ei tarkisteta.
        expect(arvo)
          .toBe(!murrettu ? "aito" : sri ? "ei ajettu" : "muutettu");
        rivit.push([murrettu ? "muutettu" : "aito",
                    sri ? "integrity" : "ei tarkistusta", arvo]);
      } finally {
        await s.sulje();
        await c.sulje();
      }
    });
  }
}
// @loppu testi

test.afterAll(() => {
  tallenna("03-sri", taulu(["CDN:n kirjasto", "sivu", "window.kirjasto"],
                           rivit));
});
