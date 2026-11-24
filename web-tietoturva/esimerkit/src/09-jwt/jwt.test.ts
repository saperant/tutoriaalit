import { test } from "node:test";
import assert from "node:assert/strict";
import { allekirjoita, allekirjoitaHmac, avainpari, tarkista,
         tarkistaHaavoittuva, type Odotukset } from "./jwt.ts";

const { yksityinen, julkinen } = avainpari();
const pem = julkinen.export({ type: "spki", format: "pem" }).toString();
const NYT = 1_800_000_000;
const odotukset: Odotukset = {
  avaimet: new Map([["k1", julkinen]]), iss: "https://tunnistus.example",
  aud: "kauppa", nyt: NYT, kumotut: new Set(["kumottu-1"]),
};
const perus = { iss: "https://tunnistus.example", aud: "kauppa",
                sub: "aino", exp: NYT + 300, jti: "t-1" };

// @alku hyokkaykset
test("alg=none: allekirjoitukseton token", () => {
  const otsake = Buffer.from('{"alg":"none"}').toString("base64url");
  const runko = Buffer.from(JSON.stringify({ ...perus, sub: "admin" }))
    .toString("base64url");
  const vaarennos = `${otsake}.${runko}.`;
  assert.equal(tarkistaHaavoittuva(vaarennos, pem).sub, "admin");
  assert.throws(() => tarkista(vaarennos, odotukset), /muoto|algoritmi/);
});

test("avainsekaannus: HS256 julkisella avaimella", () => {
  // Julkinen avain on julkinen: hyökkääjä käyttää sitä HMAC-salaisuutena.
  const vaarennos = allekirjoitaHmac({ ...perus, sub: "admin" }, pem);
  assert.equal(tarkistaHaavoittuva(vaarennos, pem).sub, "admin");
  assert.throws(() => tarkista(vaarennos, odotukset), /algoritmi/);
});

test("vanhentunut, väärä yleisö ja kumottu token", () => {
  const vanha = allekirjoita({ ...perus, exp: NYT - 3600 }, yksityinen, "k1");
  assert.equal(tarkistaHaavoittuva(vanha, pem).sub, "aino");
  assert.throws(() => tarkista(vanha, odotukset), /vanhentunut/);
  const muu = allekirjoita({ ...perus, aud: "toinen" }, yksityinen, "k1");
  assert.throws(() => tarkista(muu, odotukset), /iss\/aud/);
  const kumottu = allekirjoita({ ...perus, jti: "kumottu-1" },
                               yksityinen, "k1");
  assert.throws(() => tarkista(kumottu, odotukset), /kumottu/);
  const oikea = allekirjoita(perus, yksityinen, "k1");
  assert.equal(tarkista(oikea, odotukset).sub, "aino");
});
// @loppu hyokkaykset
