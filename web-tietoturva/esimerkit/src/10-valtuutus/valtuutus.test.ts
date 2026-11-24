import { test } from "node:test";
import assert from "node:assert/strict";
import { kaynnista } from "../http.ts";
import { api } from "./api.ts";

// @alku testit
for (const korjattu of [false, true]) {
  test(`valtuutus, ${korjattu ? "korjattu" : "haavoittuva"}`, async () => {
    const s = await kaynnista(api(korjattu));
    const kutsu = (kayttaja: string, metodi: string, polku: string,
                   runko?: unknown) =>
      fetch(`${s.url}${polku}`, { method: metodi,
        headers: { Authorization: `Bearer ${kayttaja}` },
        body: runko === undefined ? undefined : JSON.stringify(runko) });
    try {
      // BOLA: Aino vaihtaa osoitteen numeron ja näkee Villen tilauksen.
      assert.equal((await kutsu("aino", "GET", "/tilaukset/1")).status, 200);
      assert.equal((await kutsu("aino", "GET", "/tilaukset/2")).status,
                   korjattu ? 404 : 200);
      // Massamääritys: rooli kulkee samassa JSONissa kuin sähköposti.
      const minä = await (await kutsu("aino", "PATCH", "/oma",
        { sahkoposti: "uusi@x.fi", rooli: "yllapitaja" })).json();
      assert.equal(minä.sahkoposti, "uusi@x.fi");
      assert.equal(minä.rooli, korjattu ? "asiakas" : "yllapitaja");
      // Funktiotaso: asiakas kutsuu ylläpidon toimintoa suoraan.
      assert.equal((await kutsu("ville", "DELETE", "/tilaukset/2")).status,
                   korjattu ? 403 : 204);
      assert.equal((await kutsu("paula", "GET", "/tilaukset/2")).status,
                   korjattu ? 200 : 404);
    } finally {
      await s.sulje();
    }
  });
}
// @loppu testit
