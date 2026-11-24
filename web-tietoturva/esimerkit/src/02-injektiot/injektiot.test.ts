import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, readdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { BlockList } from "node:net";
import { kaynnista } from "../http.ts";
import { tietokanta, tilauksetHaavoittuva, tilaukset } from "./sql.ts";
import { kirjauduHaavoittuva, kirjaudu } from "./nosql.ts";
import { kokoHaavoittuva, koko } from "./komento.ts";
import { esikatseluHaavoittuva, esikatselu } from "./ssrf.ts";

// @alku sql
test("SQL-injektio: OR 1=1 palauttaa kaikkien tilaukset", () => {
  const db = tietokanta();
  const hyokkays = "x' OR '1'='1";
  assert.equal(tilauksetHaavoittuva(db, hyokkays).length, 4);
  assert.equal(tilaukset(db, hyokkays).length, 0);
  assert.equal(tilaukset(db, "aino").length, 2);
  assert.throws(() => tilaukset(db, "aino", "summa; DROP TABLE tilaus"));
});
// @loppu sql

// @alku nosql
test("NoSQL-injektio: operaattori ohittaa salasanan", () => {
  const runko = '{"tunnus": "admin", "salasana": {"$ne": null}}';
  assert.equal(kirjauduHaavoittuva(runko), "admin");
  assert.equal(kirjaudu(runko), null);
  assert.equal(
    kirjaudu('{"tunnus": "aino", "salasana": "kissa-ja-koira-2"}'), "aino");
});
// @loppu nosql

// @alku komento
test("komentoinjektio: ; käynnistää toisen komennon", async () => {
  const hak = await mkdtemp(path.join(tmpdir(), "wt-"));
  await writeFile(path.join(hak, "raportti.txt"), "12345");
  const hyokkays = "raportti.txt; touch PWNED";
  await kokoHaavoittuva(hak, hyokkays);
  assert.ok((await readdir(hak)).includes("PWNED"));

  const toinen = await mkdtemp(path.join(tmpdir(), "wt-"));
  await writeFile(path.join(toinen, "raportti.txt"), "12345");
  await assert.rejects(koko(toinen, hyokkays));
  assert.deepEqual(await readdir(toinen), ["raportti.txt"]);
  assert.equal(await koko(toinen, "raportti.txt"), "5 raportti.txt");
});
// @loppu komento

// @alku ssrf
test("SSRF: esikatselu ei pääse sisäverkon palveluun", async (t) => {
  // "Sisäinen" palvelu kuuntelee osoitteessa 127.0.0.1 ja "julkinen"
  // osoitteessa 127.0.0.2, joka uudelleenohjaa sisäverkkoon.
  const sisainen = await kaynnista(() => ({ runko: "salainen-avain" }));
  const julkinen = await kaynnista(() => ({
    tila: 302, otsakkeet: { Location: `${sisainen.url}/` } }), "127.0.0.2");
  t.after(async () => { await sisainen.sulje(); await julkinen.sulje(); });

  assert.equal(await esikatseluHaavoittuva(sisainen.url),
               "salainen-avain");
  assert.equal(await esikatseluHaavoittuva(julkinen.url),
               "salainen-avain");

  // Testissä sisäverkko on 127.0.0.1 ja ::1 (localhost voi ratketa
  // kumpaan tahansa); oletuslista estäisi kaiken loopbackin, myös
  // "julkisen" palvelimen.
  const estetyt = new BlockList();
  estetyt.addAddress("127.0.0.1");
  estetyt.addAddress("::1", "ipv6");
  const portti = new URL(sisainen.url).port;
  for (const kohde of [sisainen.url, `http://2130706433:${portti}/`,
                       `http://localhost:${portti}/`, "file:///etc/passwd",
                       julkinen.url]) {
    await assert.rejects(esikatselu(kohde, estetyt), kohde);
  }
});
// @loppu ssrf
