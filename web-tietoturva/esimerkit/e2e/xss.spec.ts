import { test, expect, type Page } from "@playwright/test";
import { kaynnista, type Palvelin } from "../src/http.ts";
import { palsta, type Puolustus } from "../src/03-xss/xss.ts";

// Hyökkäys onnistuu, jos sivulle ujutettu koodi asettaa
// window.pwned-muuttujan.
const SKRIPTI = "<script>window.pwned = 1</script>";
const KUVA = "<img src=x onerror='window.pwned = 1'>";

async function hyokkaa(page: Page, url: string): Promise<boolean> {
  await page.goto(url);
  return page.evaluate(() => "pwned" in window);
}

async function palvelin(p: Puolustus): Promise<Palvelin> {
  return kaynnista(palsta(p));
}

// @alku testit
const TAPAUKSET: [string, Puolustus, boolean][] = [
  ["ei puolustusta", { escapoi: false, csp: false }, true],
  ["vain CSP", { escapoi: false, csp: true }, false],
  ["koodaus ja CSP", { escapoi: true, csp: true }, false],
];

for (const [nimi, puolustus, onnistuu] of TAPAUKSET) {
  test(`XSS, ${nimi}`, async ({ page }) => {
    const s = await palvelin(puolustus);
    try {
      // Heijastettu: hyötykuorma hakuparametrissa.
      const q = encodeURIComponent(KUVA);
      expect(await hyokkaa(page, `${s.url}/?q=${q}`)).toBe(onnistuu);
      // DOM-pohjainen: hyötykuorma fragmentissa, ei koskaan palvelimelle.
      expect(await hyokkaa(page, `${s.url}/#${encodeURIComponent(KUVA)}`))
        .toBe(onnistuu);
      // Tallennettu: kommentti lomakkeen kautta.
      await page.goto(s.url);
      await page.fill("input[name=teksti]", SKRIPTI);
      await page.click("button");
      expect(await page.evaluate(() => "pwned" in window)).toBe(onnistuu);
    } finally {
      await s.sulje();
    }
  });
}
// @loppu testit

// @alku tt
test("Trusted Types estää merkkijonon innerHTML-sijoituksen", async ({
  page,
}) => {
  // Vain CSP päällä: DOM-sijoitus innerHTML:ään kaatuu poikkeukseen
  // ennen kuin hyötykuorma ehtii DOM:iin.
  const s = await palvelin({ escapoi: false, csp: true });
  const virheet: string[] = [];
  page.on("pageerror", (v) => virheet.push(v.message));
  try {
    await page.goto(`${s.url}/#Aino`);
    expect(virheet.join()).toContain("TrustedHTML");
  } finally {
    await s.sulje();
  }
});
// @loppu tt
