import { test, expect, type Page } from "@playwright/test";
import { kaynnista, type Palvelin } from "../src/http.ts";
import { palsta, type Puolustus } from "../src/03-xss/xss.ts";
import { taulu, tallenna } from "../src/taulu.ts";

// Näytöstaulu (naytos/03-xss.odotettu): reitti x kokoonpano.
const REITIT = ["heijastettu", "DOM-pohjainen", "tallennettu"];
const tulokset = new Map<string, string[]>();
const kirjaa = (nimi: string, ajettiin: boolean) =>
  tulokset.set(nimi, [...(tulokset.get(nimi) ?? []),
                      ajettiin ? "ajettiin" : "estetty"]);

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
  ["vain koodaus", { escapoi: true, csp: false }, false],
  ["vain CSP", { escapoi: false, csp: true }, false],
  ["koodaus ja CSP", { escapoi: true, csp: true }, false],
];

for (const [nimi, puolustus, onnistuu] of TAPAUKSET) {
  test(`XSS, ${nimi}`, async ({ page }) => {
    const s = await palvelin(puolustus);
    try {
      // Heijastettu: hyötykuorma hakuparametrissa.
      const q = encodeURIComponent(KUVA);
      const heijastettu = await hyokkaa(page, `${s.url}/?q=${q}`);
      // DOM-pohjainen: hyötykuorma fragmentissa, ei koskaan palvelimelle.
      const dom = await hyokkaa(page,
                                `${s.url}/#${encodeURIComponent(KUVA)}`);
      // Tallennettu: kommentti lomakkeen kautta.
      await page.goto(s.url);
      await page.fill("input[name=teksti]", SKRIPTI);
      await page.click("button");
      const tallennettu = await page.evaluate(() => "pwned" in window);
      expect([heijastettu, dom, tallennettu])
        .toEqual([onnistuu, onnistuu, onnistuu]);
      for (const t of [heijastettu, dom, tallennettu]) kirjaa(nimi, t);
    } finally {
      await s.sulje();
    }
  });
}
// @loppu testit

test.afterAll(() => {
  const sarakkeet = [...tulokset.keys()];
  tallenna("03-xss", taulu(["reitti", ...sarakkeet], REITIT.map((r, i) =>
    [r, ...sarakkeet.map((s) => tulokset.get(s)![i]!)])));
});

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
