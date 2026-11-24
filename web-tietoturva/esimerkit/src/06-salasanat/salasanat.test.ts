import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { kaynnista } from "../http.ts";
import { tiivista, tarkista, arvioi, vuotanut } from "./salasanat.ts";
import { Kirjautuminen, Rajoitin } from "./kirjautuminen.ts";

test("tiiviste: suolattu, tarkistettava, parametrit mukana", () => {
  const a = tiivista("oikea hevonen akku niitti");
  const b = tiivista("oikea hevonen akku niitti");
  assert.notEqual(a, b);                         // eri suola
  assert.ok(a.startsWith("scrypt$32768$8$1$"));
  assert.ok(tarkista("oikea hevonen akku niitti", a));
  assert.ok(!tarkista("oikea hevonen akku nitti", a));
});

// @alku kaytanto-testi
test("käytäntö: pituus ja estolista, ei merkkiluokkia", () => {
  const estetyt = new Set(["salasana123456789"]);
  assert.deepEqual(arvioi("Kesä2026!", "aino", estetyt),
                   ["vähintään 15 merkkiä"]);
  assert.deepEqual(arvioi("salasana123456789", "aino", estetyt),
                   ["yleinen tai vuotanut"]);
  assert.deepEqual(arvioi("aino-sanoo-hyvää-huomenta", "aino", estetyt),
                   ["sisältää käyttäjätunnuksen"]);
  assert.deepEqual(arvioi("lumi sataa hiljaa pihalle", "aino", estetyt),
                   []);
});
// @loppu kaytanto-testi

// @alku kanon-testi
test("k-anonymiteetti: palvelu näkee vain viisi merkkiä", async (t) => {
  const sana = "qwerty123";
  const sha = createHash("sha1").update(sana).digest("hex").toUpperCase();
  const pyydetyt: string[] = [];
  const palvelu = await kaynnista((p) => {
    pyydetyt.push(p.polku);
    // Vastaus: kaikki tunnetut loppuosat, joilla on sama etuliite.
    return { runko: "0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n" +
                    `${sha.slice(5)}:3912816\r\n` };
  });
  t.after(() => palvelu.sulje());
  assert.equal(await vuotanut(sana, palvelu.url), 3912816);
  assert.equal(await vuotanut("lumi sataa hiljaa pihalle", palvelu.url), 0);
  assert.deepEqual(pyydetyt[0], `/range/${sha.slice(0, 5)}`);
});
// @loppu kanon-testi

// @alku arvailu
test("tunnusten arvailu: sama vastaus ja sama työ", () => {
  const k = new Kirjautuminen({ aino: "lumi sataa hiljaa pihalle" });
  assert.notEqual(k.haavoittuva("ville", "x").viesti,
                  k.haavoittuva("aino", "x").viesti);
  const ennen = k.tiivistyksia;
  assert.deepEqual(k.kirjaudu("ville", "x", "10.0.0.1"),
                   k.kirjaudu("aino", "x", "10.0.0.1"));
  assert.equal(k.tiivistyksia - ennen, 2);       // myös tuntematon
});
// @loppu arvailu

// @alku rajoitus
test("nopeusrajoitus: viisi yritystä, sitten yksi minuutissa", () => {
  let nyt = 0;
  const r = new Rajoitin(5, 1 / 60, () => nyt);
  const tulokset = Array.from({ length: 7 }, () => r.salli("aino"));
  assert.deepEqual(tulokset, [true, true, true, true, true, false, false]);
  nyt += 60_000;
  assert.equal(r.salli("aino"), true);
  assert.equal(r.salli("aino"), false);
  assert.equal(r.salli("ville"), true);          // eri avain
});
// @loppu rajoitus
