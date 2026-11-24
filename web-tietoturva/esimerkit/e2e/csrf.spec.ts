import { test, expect, type Page } from "@playwright/test";
import { kaynnista, type Kasittelija } from "../src/http.ts";
import { pankki, hyokkaajanSivu } from "../src/04-csrf/pankki.ts";

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
      expect(await saldo(page, y.pankki)).toBe("Saldo: 1000 €");
      await page.goto(`${y.hyokkaaja}/#csrf`);     // uhri avaa sivun
      await page.waitForLoadState("networkidle");
      expect(await saldo(page, y.pankki))
        .toBe(korjattu ? "Saldo: 1000 €" : "Saldo: 500 €");
      // Oma lomake toimii edelleen.
      await page.fill("input[name=saaja]", "hyokkaaja");
      await page.fill("input[name=summa]", "100");
      await page.click("button");
      expect(await page.textContent("p"))
        .toBe(korjattu ? "Saldo: 900 €" : "Saldo: 400 €");
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
    } finally {
      await y.sulje();
    }
  });
}
// @loppu clickjacking
