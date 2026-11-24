import { test } from "node:test";
import assert from "node:assert/strict";
import { kaynnista } from "../http.ts";
import { palsta } from "../03-xss/xss.ts";
import { skannaa } from "./skanneri.ts";

// @alku testi
test("skanneri löytää haavoittuvan palstan puutteet", async () => {
  const huono = await kaynnista(palsta({ escapoi: false, csp: false }));
  const hyva = await kaynnista(palsta({ escapoi: true, csp: true }));
  try {
    assert.deepEqual(await skannaa(huono.url, ["/?q=kahvi"]), [
      { kohde: "/", ongelma: "puuttuu Content-Security-Policy" },
      { kohde: "/", ongelma: "puuttuu kehystyssuojaus" },
      { kohde: "/", ongelma: "puuttuu X-Content-Type-Options" },
      { kohde: "/", ongelma: "parametri q heijastuu koodaamatta" },
    ]);
    // Korjatussa versiossa XSS on torjuttu, mutta skanneri muistuttaa
    // vielä kahdesta otsakkeesta (ks. luku 11).
    assert.deepEqual((await skannaa(hyva.url, ["/?q=kahvi"]))
      .map((h) => h.ongelma), [
      "puuttuu kehystyssuojaus", "puuttuu X-Content-Type-Options"]);
  } finally {
    await huono.sulje();
    await hyva.sulje();
  }
});
// @loppu testi
