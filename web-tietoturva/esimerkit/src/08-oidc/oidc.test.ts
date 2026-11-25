import { test } from "node:test";
import assert from "node:assert/strict";
import { kaynnista } from "../http.ts";
import { tarjoaja } from "./tarjoaja.ts";
import { Selain, ymparisto } from "./selain.ts";

// @alku kirjautumis-csrf
for (const korjattu of [false, true]) {
  test(`kirjautumis-CSRF, ${korjattu ? "korjattu" : "haavoittuva"}`,
       async () => {
    const y = await ymparisto(korjattu);
    try {
      // Normaali kirjautuminen toimii.
      const aino = new Selain("aino", y.idp);
      await aino.hae(`${y.kauppa}/kirjaudu`);
      assert.deepEqual(await (await aino.hae(y.kauppa)).json(),
                       { kayttaja: "aino" });

      // Hyökkääjä aloittaa virran omilla tunnuksillaan ja pysähtyy
      // ennen paluuta: hänellä on oman tilinsä koodi ja state.
      const h = new Selain("hyokkaaja", y.idp);
      const ohjaus = await h.hae(`${y.kauppa}/kirjaudu`, false);
      const idpVastaus = await h.hae(ohjaus.headers.get("location")!, false);
      const ansa = idpVastaus.headers.get("location")!;

      // Uhri avaa ansalinkin ja kirjautuu hyökkääjän tilille.
      const uhri = new Selain("uhri", y.idp);
      const tulos = await uhri.hae(ansa);
      if (korjattu) {
        assert.equal(tulos.status, 400);          // state ei täsmää
      } else {
        assert.deepEqual(await tulos.json(), { kayttaja: "hyokkaaja" });
      }
    } finally {
      await y.sulje();
    }
  });
}
// @loppu kirjautumis-csrf

// @alku pkce
for (const tiukka of [false, true]) {
  test(`varastettu koodi, PKCE ${tiukka ? "vaaditaan" : "ei käytössä"}`,
       async () => {
    const y = await ymparisto(tiukka);
    try {
      // Hyökkääjä kaappaa uhrin koodin paluuosoitteesta (esim. lokista,
      // Referer-otsakkeesta tai haitallisesta sovelluksesta).
      const uhri = new Selain("aino", y.idp);
      const ohjaus = await uhri.hae(`${y.kauppa}/kirjaudu`, false);
      const paluu = new URL((await uhri.hae(ohjaus.headers.get("location")!,
                                            false)).headers.get("location")!);
      const vastaus = await fetch(`${y.idp}/token`, { method: "POST",
        body: new URLSearchParams({ grant_type: "authorization_code",
          client_id: "kauppa", redirect_uri: `${y.kauppa}/paluu`,
          code: paluu.searchParams.get("code")! }) });
      assert.equal(vastaus.status, tiukka ? 400 : 200);
    } finally {
      await y.sulje();
    }
  });
}
// @loppu pkce

// @alku paluuosoite-testi
test("paluuosoite: alkuosan vertailu vuotaa koodin", async () => {
  const asiakkaat = new Map([["kauppa", "https://kauppa.example"]]);
  const hyokkays = "https://kauppa.example.hyokkaaja.example/";
  for (const tiukka of [false, true]) {
    const s = await kaynnista(tarjoaja("x", asiakkaat, tiukka));
    const u = new URL(`${s.url}/authorize`);
    u.search = new URLSearchParams({ client_id: "kauppa",
      redirect_uri: hyokkays, response_type: "code", state: "s",
      code_challenge: "x".repeat(43), code_challenge_method: "S256" })
      .toString();
    const v = await fetch(u, { redirect: "manual" });
    assert.equal(v.status, tiukka ? 400 : 302);
    if (!tiukka) assert.ok(v.headers.get("location")!.startsWith(hyokkays));
    await s.sulje();
  }
});
// @loppu paluuosoite-testi
