// Yksi testisarja kaikille toteutuksille. Testit puhuvat sovellukselle
// kuten käyttäjä: roolit, nimet ja näkyvä teksti. Kehys ei näy niissä.
import { expect, test, type Page } from "@playwright/test";

// @alku alku
test.beforeEach(async ({ page }, tiedot) => {
  await page.goto(`${process.env.SOVELLUKSET}/${tiedot.project.name}/`);
});

const lista = (page: Page) => page.getByRole("list", { name: "Tehtävät" });
const rivit = (page: Page) => lista(page).getByRole("listitem");
const nimi = (page: Page) => page.getByRole("textbox", { name: "Tehtävä" });
const lisaa = (page: Page) => page.getByRole("button", { name: "Lisää" });

type Kasittelija = Parameters<Page["route"]>[1];

/** Lataa sivun uudelleen niin, että alkutila haetaan taas palvelimelta
 *  ja pyyntö kulkee annetun käsittelijän kautta. */
async function lataaUudelleen(page: Page, kasittelija: Kasittelija) {
  await expect(rivit(page)).toHaveCount(3);     // ensimmäinen lataus ohi
  await page.route("**/tehtavat.json", kasittelija);
  await page.evaluate(() => { localStorage.clear(); });
  await page.reload();
}
// @loppu alku

// @alku rakenne
test("rakenne on sama joka toteutuksessa", async ({ page }) => {
  await expect(rivit(page)).toHaveCount(3);
  await expect(page.locator("body")).toMatchAriaSnapshot(`
    - banner:
      - heading "Tehtävät" [level=1]
      - status: 2 avointa, 1 valmis
    - main:
      - form "Uusi tehtävä":
        - text: Tehtävä
        - textbox "Tehtävä"
        - text: Kiireellisyys
        - combobox "Kiireellisyys":
          - option "Tavallinen" [selected]
          - option "Kiireellinen"
        - button "Lisää"
        - alert
      - group "Näytä":
        - text: Näytä
        - radio "Kaikki" [checked]
        - text: Kaikki
        - radio "Avoimet"
        - text: Avoimet
        - radio "Valmiit"
        - text: Valmiit
      - list "Tehtävät":
        - listitem:
          - checkbox "Varaa kokoushuone"
          - text: Varaa kokoushuone kiireellinen
          - button "Poista Varaa kokoushuone"
        - listitem:
          - checkbox "Lähetä esityslista" [checked]
          - text: Lähetä esityslista
          - button "Poista Lähetä esityslista"
        - listitem:
          - checkbox "Tilaa kahvit"
          - text: Tilaa kahvit
          - button "Poista Tilaa kahvit"
      - button "Poista valmiit"
  `);
  await expect(page).toHaveTitle("Tehtävät (2)");
});
// @loppu rakenne

test("lataus näkyy ja virheestä toivutaan", async ({ page }) => {
  let pyyntoja = 0;
  await lataaUudelleen(page, async (reitti) => {
    pyyntoja += 1;
    if (pyyntoja === 1) await reitti.fulfill({ status: 500 });
    else await reitti.continue();
  });
  const virhe = page.getByText("Tehtävien lataus epäonnistui.");
  await expect(virhe).toBeVisible();
  await expect(virhe).toHaveRole("alert");
  await expect(lista(page)).toHaveCount(0);

  await page.getByRole("button", { name: "Yritä uudelleen" }).click();
  await expect(rivit(page)).toHaveCount(3);
  await expect(virhe).toHaveCount(0);
});

test("latauksen aikana näytetään ilmoitus", async ({ page }) => {
  let paasta = () => {};
  const lupa = new Promise<void>((valmis) => { paasta = valmis; });
  await lataaUudelleen(page, async (reitti) => {
    await lupa;
    await reitti.continue();
  });
  await expect(page.getByText("Ladataan tehtäviä…")).toBeVisible();
  paasta();
  await expect(rivit(page)).toHaveCount(3);
  await expect(page.getByText("Ladataan tehtäviä…")).toHaveCount(0);
});

// @alku lomake
test("lomake validoi ja lisää tehtävän", async ({ page }) => {
  const virhe = page.getByRole("form").getByRole("alert");
  await expect(rivit(page)).toHaveCount(3);

  // Virhettä ei näytetä ennen ensimmäistä lähetysyritystä.
  await nimi(page).fill("ab");
  await expect(virhe).toBeEmpty();
  await lisaa(page).click();
  await expect(virhe)
    .toHaveText("Nimessä on oltava vähintään 3 merkkiä.");
  await expect(nimi(page)).toHaveAttribute("aria-invalid", "true");
  await expect(nimi(page)).toBeFocused();

  // Yrityksen jälkeen virhe seuraa kenttää näppäily kerrallaan.
  await nimi(page).fill("tilaa KAHVIT");
  await expect(virhe).toHaveText("Samanniminen tehtävä on jo listalla.");
  await nimi(page).fill("Kirjoita muistio");
  await expect(virhe).toBeEmpty();
  await expect(nimi(page)).toHaveAttribute("aria-invalid", "false");

  await page.getByRole("combobox", { name: "Kiireellisyys" })
    .selectOption("kiireellinen");
  await nimi(page).press("Enter");
  await expect(rivit(page)).toHaveCount(4);
  await expect(rivit(page).last().getByRole("checkbox"))
    .toHaveAccessibleName("Kirjoita muistio");
  await expect(rivit(page).last().locator(".merkki"))
    .toHaveText("kiireellinen");
  await expect(nimi(page)).toHaveValue("");
  await expect(nimi(page)).toBeFocused();
  await expect(page.getByRole("status")).toHaveText("3 avointa, 1 valmis");
});
// @loppu lomake

test("valmiiksi merkitseminen päivittää yhteenvedon", async ({ page }) => {
  await page.getByRole("checkbox", { name: "Tilaa kahvit" }).check();
  await expect(page.getByRole("status")).toHaveText("1 avoin, 2 valmista");
  await expect(page).toHaveTitle("Tehtävät (1)");
  await expect(rivit(page).last()).toHaveClass(/valmis/);

  await page.getByRole("checkbox", { name: "Tilaa kahvit" }).uncheck();
  await expect(page.getByRole("status")).toHaveText("2 avointa, 1 valmis");
});

test("suodatin rajaa näkyvät tehtävät", async ({ page }) => {
  await page.getByRole("radio", { name: "Avoimet" }).check();
  await expect(rivit(page)).toHaveCount(2);
  await page.getByRole("radio", { name: "Valmiit" }).check();
  await expect(rivit(page)).toHaveText([/Lähetä esityslista/]);

  // Viimeisen valmiin poistaminen tyhjentää näkymän mutta ei listaa.
  await page.getByRole("button", { name: "Poista valmiit" }).click();
  await expect(page.getByText("Ei näytettäviä tehtäviä.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Poista valmiit" }))
    .toBeDisabled();
  await page.getByRole("radio", { name: "Kaikki" }).check();
  await expect(rivit(page)).toHaveCount(2);
});

// @alku avaimet
test("poisto säilyttää muiden rivien DOM-solmut", async ({ page }) => {
  await expect(rivit(page)).toHaveCount(3);
  // Merkitään kolmas rivi suoraan DOM:iin. Jos lista piirrettäisiin
  // uudelleen tai rivit kierrätettäisiin järjestysnumeron mukaan,
  // merkki katoaisi tai päätyisi väärälle riville.
  await rivit(page).nth(2).evaluate((li) => { li.dataset.merkki = "x"; });
  await page.getByRole("button", { name: "Poista Varaa kokoushuone" })
    .click();
  await expect(rivit(page)).toHaveCount(2);
  await expect(page.locator("li[data-merkki]")).toContainText(
    "Tilaa kahvit");
});
// @loppu avaimet

// @alku pysyvyys
test("muutokset säilyvät sivun latauksen yli", async ({ page }) => {
  await nimi(page).fill("Kirjoita muistio");
  await lisaa(page).click();
  await page.getByRole("checkbox", { name: "Lähetä esityslista" })
    .uncheck();
  // Tallennus on sivuvaikutus, jonka kehys ajaa omalla hetkellään.
  // Otsikko päivittyy samassa efektissä, joten sitä voi odottaa.
  await expect(page).toHaveTitle("Tehtävät (4)");

  await page.reload();
  await expect(rivit(page)).toHaveCount(4);
  await expect(page.getByRole("checkbox", { name: "Lähetä esityslista" }))
    .not.toBeChecked();
  await expect(page.getByRole("status"))
    .toHaveText("4 avointa, 0 valmista");
});
// @loppu pysyvyys
