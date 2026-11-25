import { test, expect, type Page } from "@playwright/test";
import { kaynnista, type Kasittelija } from "../src/http.ts";
import { pankki, hyokkaajanSivu } from "../src/04-csrf/pankki.ts";
import { taulu, tallenna } from "../src/taulu.ts";

// Näytöstaulu (naytos/04-csrf.odotettu).
const VAIHEET = ["saldo kirjautuessa", "saldo hyökkääjän sivun jälkeen",
                 "saldo oman 100 euron siirron jälkeen",
                 "pankin painike hyökkääjän kehyksessä"];
const tulokset: string[][] = [[], []];

// Pankki on osoitteessa localhost ja hyökkääjä osoitteessa
// 127.0.0.1: selaimelle ne ovat eri sivustoja (site).
async function ymparisto(korjattu: boolean) {
  // Pankin Origin-tarkistus tarvitsee oman osoitteensa, joten käsittelijä
  // luodaan vasta, kun palvelimen portti on tiedossa.
  let kasittelija: Kasittelija = () => ({});
  const p = await kaynnista((pyynto) => kasittelija(pyynto));
  const alkupera = p.url.replace("127.0.0.1", "localhost");
  kasittelija = pankki(korjattu, alkupera);
  const h = await kaynnista(hyokkaajanSivu(alkupera));
  return { pankki: alkupera, hyokkaaja: h.url,
           sulje: async () => { await p.sulje(); await h.sulje(); } };
}

async function saldo(page: Page, url: string): Promise<string> {
  await page.goto(url);
  return (await page.textContent("p")) ?? "";
}

// @alku csrf
for (const korjattu of [false, true]) {
  test(`CSRF, ${korjattu ? "korjattu" : "haavoittuva"}`, async ({
    page,
  }) => {
    const y = await ymparisto(korjattu);
    try {
      await page.goto(`${y.pankki}/kirjaudu`);
      const alussa = await saldo(page, y.pankki);
      expect(alussa).toBe("Saldo: 1000 €");
      await page.goto(`${y.hyokkaaja}/#csrf`);     // uhri avaa sivun
      await page.waitForLoadState("networkidle");
      const hyokkayksenJalkeen = await saldo(page, y.pankki);
      expect(hyokkayksenJalkeen)
        .toBe(korjattu ? "Saldo: 1000 €" : "Saldo: 500 €");
      // Oma lomake toimii edelleen.
      await page.fill("input[name=saaja]", "hyokkaaja");
      await page.fill("input[name=summa]", "100");
      await page.click("button");
      const lopussa = await page.textContent("p");
      expect(lopussa).toBe(korjattu ? "Saldo: 900 €" : "Saldo: 400 €");
      tulokset[Number(korjattu)]!.push(
        ...[alussa, hyokkayksenJalkeen, lopussa ?? ""]
          .map((s) => s.replace("Saldo: ", "")));
    } finally {
      await y.sulje();
    }
  });
}
// @loppu csrf

// @alku clickjacking
for (const korjattu of [false, true]) {
  test(`clickjacking, ${korjattu ? "korjattu" : "haavoittuva"}`, async ({
    page,
  }) => {
    const y = await ymparisto(korjattu);
    try {
      await page.goto(`${y.pankki}/kirjaudu`);
      await page.goto(y.hyokkaaja);
      const kehys = page.frameLocator("#k");
      await expect(kehys.locator("button")).toHaveCount(korjattu ? 0 : 1);
      tulokset[Number(korjattu)]!.push(
        await kehys.locator("button").count() ? "latautuu" : "ei lataudu");
    } finally {
      await y.sulje();
    }
  });
}
// @loppu clickjacking

test.afterAll(() => {
  tallenna("04-csrf", taulu(["vaihe", "haavoittuva", "korjattu"],
    VAIHEET.map((v, i) => [v, tulokset[0]![i]!, tulokset[1]![i]!])));
});
