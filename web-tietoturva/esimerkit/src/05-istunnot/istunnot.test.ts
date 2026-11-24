import { test } from "node:test";
import assert from "node:assert/strict";
import { kaynnista } from "../http.ts";
import { Istunnot, palvelu, EVASTE, evaste } from "./istunnot.ts";

function evasteesta(v: Response): string {
  const otsake = v.headers.get("set-cookie") ?? "";
  return otsake.slice(`${EVASTE}=`.length, otsake.indexOf(";"));
}

// @alku kiinnitys
for (const korjattu of [false, true]) {
  test(`istunnon kiinnitys, ${korjattu ? "korjattu" : "haavoittuva"}`,
       async () => {
    const s = await kaynnista(palvelu(korjattu));
    try {
      // 1) Hyökkääjä hankkii anonyymin tunnisteen ja houkuttelee uhrin
      //    kirjautumaan linkistä, jossa tunniste on mukana.
      const sid = await (await fetch(`${s.url}/uusi`)).text();
      const v = await fetch(`${s.url}/kirjaudu?sid=${sid}`, {
        method: "POST", body: "tunnus=aino" });
      const uhrin = evasteesta(v);
      // 2) Hyökkääjä käyttää omaa tunnistettaan.
      const tulos = await fetch(`${s.url}/?sid=${sid}`);
      assert.equal(tulos.status, korjattu ? 401 : 200);
      assert.equal(uhrin === sid, !korjattu);
    } finally {
      await s.sulje();
    }
  });
}
// @loppu kiinnitys

// @alku vanheneminen
test("istunto vanhenee jouto- ja enimmäisajan mukaan", () => {
  let nyt = 0;
  const ist = new Istunnot(() => nyt, 15 * 60_000, 8 * 3600_000);
  const id = ist.luo("aino");
  nyt = 14 * 60_000;
  assert.ok(ist.hae(id));                       // käyttö jatkaa aikaa
  nyt += 14 * 60_000;
  assert.ok(ist.hae(id));
  nyt += 16 * 60_000;
  assert.equal(ist.hae(id), undefined);          // joutoaika ylittyi

  const toinen = ist.luo("aino");
  for (let i = 0; i < 40; i++) { nyt += 14 * 60_000; ist.hae(toinen); }
  assert.equal(ist.hae(toinen), undefined);      // enimmäisaika
});
// @loppu vanheneminen

test("uloskirjautuminen mitätöi istunnon palvelimella", async () => {
  const s = await kaynnista(palvelu(true));
  try {
    const v = await fetch(`${s.url}/kirjaudu`, {
      method: "POST", body: "tunnus=aino" });
    const sid = evasteesta(v);
    const pyynto = { headers: { Cookie: `${EVASTE}=${sid}` } };
    assert.equal((await fetch(s.url, pyynto)).status, 200);
    await fetch(`${s.url}/ulos`, { method: "POST", ...pyynto });
    // Varastettu eväste ei enää kelpaa, vaikka selain olisi tallentanut
    // sen.
    assert.equal((await fetch(s.url, pyynto)).status, 401);
    assert.match(evaste("x"), /Secure; HttpOnly; SameSite=Lax/);
  } finally {
    await s.sulje();
  }
});
