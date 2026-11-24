import type { Page, Route } from "@playwright/test";
import { TILAT } from "../src/tilat.ts";

// @alku mokki
/** Mokattu rajapinta: testi päättää vastaukset, ja testi on nopea ja
 *  toistettava ilman palvelinta. Palauttaa lähetetyt varaukset. */
export async function mokkaaApi(page: Page) {
  const varaukset: unknown[] = [];
  await page.route("**/api/tilat", (r) => r.fulfill({ json: TILAT }));
  await page.route("**/api/tilat/*", (r: Route) => {
    const id = new URL(r.request().url()).pathname.split("/").at(-1);
    const tila = TILAT.find((t) => t.id === id);
    return tila ? r.fulfill({ json: tila })
                : r.fulfill({ status: 404, json: { virhe: "Ei löydy." } });
  });
  await page.route("**/api/varaukset", async (r) => {
    varaukset.push(r.request().postDataJSON());
    await r.fulfill({ status: 201, json: { id: "v7" } });
  });
  return varaukset;
}
// @loppu mokki
