import { expect, test } from "@playwright/test";
import { TILAT } from "../src/tilat.ts";

// @alku virheet
test("palvelinvirheestä toivutaan uudella yrityksellä", async ({ page }) => {
  let kutsuja = 0;
  await page.route("**/api/tilat", (r) => {
    kutsuja += 1;
    return kutsuja === 1
      ? r.fulfill({ status: 503, json: { virhe: "Huoltokatko" } })
      : r.fulfill({ json: TILAT });
  });
  await page.goto("/");
  await expect(page.getByRole("alert"))
    .toContainText("Tietojen haku epäonnistui: Huoltokatko");
  await page.getByRole("button", { name: "Yritä uudelleen" }).click();
  await expect(page.getByText("4 / 4 tilaa")).toBeVisible();
});

test("katkennut yhteys näytetään virheenä", async ({ page }) => {
  await page.route("**/api/tilat", (r) => r.abort("internetdisconnected"));
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("epäonnistui");
});
// @loppu virheet
