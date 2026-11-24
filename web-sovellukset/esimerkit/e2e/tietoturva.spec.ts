import { expect, test } from "@playwright/test";
import { TILAT } from "../src/tilat.ts";

// @alku xss
test("rajapinnan HTML näkyy tekstinä eikä suoritu", async ({ page }) => {
  const nimi = `<img src=x onerror="document.title='murrettu'">`;
  await page.route("**/api/tilat", (r) =>
    r.fulfill({ json: [{ ...TILAT[0], nimi }] }));
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 3 })).toHaveText(nimi);
  await expect(page).not.toHaveTitle("murrettu");
});
// @loppu xss

// @alku csp
test("tuotantopalvelin lähettää CSP:n, joka estää inline-skriptin",
  async ({ page }) => {
    await page.route("**/api/tilat", (r) => r.fulfill({ json: TILAT }));
    const vastaus = await page.goto("/");
    expect(vastaus?.headers()["content-security-policy"])
      .toContain("script-src 'self'");

    const rikkomukset: string[] = [];
    page.on("console", (v) => {
      if (v.type() === "error") rikkomukset.push(v.text());
    });
    // Hyökkääjän injektoima inline-skripti samaan dokumenttiin:
    await page.evaluate(() => {
      const s = document.createElement("script");
      s.textContent = "document.title = 'murrettu'";
      document.body.append(s);
    });
    await expect(page).not.toHaveTitle("murrettu");
    expect(rikkomukset.join("\n")).toContain("Content Security Policy");
  });
// @loppu csp
