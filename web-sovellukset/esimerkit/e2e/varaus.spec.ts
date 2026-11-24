import { expect, test } from "@playwright/test";
import { mokkaaApi } from "./api.ts";

// @alku varaus
test("käyttäjä löytää tilan ja varaa sen", async ({ page }) => {
  const varaukset = await mokkaaApi(page);
  await page.goto("/");

  await page.getByRole("searchbox", { name: "Hae nimellä" }).fill("ki");
  await page.getByRole("button", { name: "Varaa Kivi" }).click();

  await expect(page).toHaveURL("/tilat/kivi");
  const otsikko = page.getByRole("heading", { level: 1, name: "Kivi" });
  await expect(otsikko).toBeFocused();           // fokus uuteen sivuun
  await expect(page).toHaveTitle("Kivi – Tilavaraus");

  await page.getByLabel("Aihe").fill("Sprintin katselmointi");
  await page.getByRole("button", { name: "Varaa" }).click();
  await expect(page.getByRole("status"))
    .toHaveText("Varaus tehty (tunnus v7).");
  expect(varaukset).toEqual([expect.objectContaining(
    { tilaId: "kivi", aihe: "Sprintin katselmointi", kesto: 60 })]);
});

test("selaimen Takaisin ja Eteenpäin toimivat", async ({ page }) => {
  await mokkaaApi(page);
  await page.goto("/tilat/aalto");
  await page.getByRole("link", { name: "Tilat" }).click();
  await expect(page.getByRole("heading", { name: "Kokoustilat" }))
    .toBeVisible();
  await page.goBack();
  await expect(page).toHaveURL("/tilat/aalto");
  await expect(page.getByRole("heading", { name: "Aalto" })).toBeVisible();
  await page.goForward();
  await expect(page.getByText("4 / 4 tilaa")).toBeVisible();
});
// @loppu varaus
