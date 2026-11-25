import { expect, type Page, test } from "@playwright/test";
import { mokkaaApi } from "../e2e/api.ts";

// Tutoriaalin kuvakaappaukset valmiista sovelluksesta. Rajapinta on
// mokattu kuten päästä päähän -testeissä, joten kuvat ovat toistettavia.
// Ajo: make kuvat (tallentaa hakemistoon ../kuvat).

test.use({
  viewport: { width: 760, height: 640 },   // main on 44rem:n palsta
  deviceScaleFactor: 2,                 // terävä kuva painettuna
});

/** Kuva pääsisällöstä ja yläpalkista ilman tyhjää alaosaa. Kapea
 *  sisältö (lomake) rajataan vasemmasta reunasta annettuun leveyteen.
 *  Palauttaa kuvan korkeuden, jotta rinnakkain ladottavat kuvat voi
 *  ottaa samankorkuisina (vahintaan). */
async function kuva(page: Page, nimi: string, leveys = 760,
                    vahintaan = 0) {
  const main = await page.locator("main").boundingBox();
  const korkeus = Math.max(vahintaan,
    Math.ceil((main?.y ?? 0) + (main?.height ?? 0)));
  await page.screenshot({
    path: `../kuvat/${nimi}.png`,
    fullPage: true,
    clip: { x: 0, y: 0, width: leveys, height: korkeus },
  });
  return korkeus;
}

test("tilalista ja haku", async ({ page }) => {
  await mokkaaApi(page);
  await page.goto("/");
  await expect(page.getByText("4 / 4 tilaa")).toBeVisible();
  await kuva(page, "01-tilat");

  await page.getByRole("searchbox", { name: "Hae nimellä" }).fill("ki");
  await expect(page.getByText("1 / 4 tilaa")).toBeVisible();
  await kuva(page, "04-haku");
});

test("varauslomake: tyhjä, virheet, lähetys ja valmis", async ({ page }) => {
  await mokkaaApi(page);
  // Vastaus viipyy, kunnes testi päästää sen: lähetystila ehtii kuvaan.
  let vastaa!: () => void;
  const lupa = new Promise<void>((ok) => { vastaa = ok; });
  await page.route("**/api/varaukset", async (r) => {
    await lupa;
    await r.fulfill({ status: 201, json: { id: "v7" } });
  });
  await page.clock.setFixedTime(new Date("2026-12-01T08:00:00Z"));
  await page.goto("/tilat/kivi");
  await expect(page.getByRole("heading", { name: "Kivi" })).toBeFocused();
  await kuva(page, "08-tila", 400);

  await page.getByLabel("Kesto (min)").fill("5");
  await page.getByRole("button", { name: "Varaa" }).click();
  await expect(page.getByLabel("Aihe")).toHaveAttribute(
    "aria-invalid", "true");
  const korkeus = await kuva(page, "05-virheet", 400);

  await page.getByLabel("Kesto (min)").fill("60");
  await page.getByLabel("Aihe").fill("Sprintin katselmointi");
  await page.getByRole("button", { name: "Varaa" }).click();
  await expect(page.getByRole("button", { name: "Varataan…" }))
    .toBeDisabled();
  await kuva(page, "05-lahetys", 400, korkeus);

  vastaa();
  await expect(page.getByRole("status")).toHaveText(
    "Varaus tehty (tunnus v7).");
});

test("virhetila ja uusi yritys", async ({ page }) => {
  await page.route("**/api/tilat", (r) =>
    r.fulfill({ status: 503, json: { virhe: "Huoltokatko" } }));
  await page.goto("/");
  await expect(page.getByRole("alert")).toBeVisible();
  await kuva(page, "07-virhe");
});
