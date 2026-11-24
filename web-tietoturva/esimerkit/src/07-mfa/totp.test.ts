import { test } from "node:test";
import assert from "node:assert/strict";
import { totp, TotpTarkistin } from "./totp.ts";

// @alku testi
test("TOTP: RFC 6238:n testivektorit (SHA-1, 8 numeroa)", () => {
  const salaisuus = Buffer.from("12345678901234567890");
  assert.equal(totp(salaisuus, 59, 8), "94287082");
  assert.equal(totp(salaisuus, 1111111109, 8), "07081804");
  assert.equal(totp(salaisuus, 1234567890, 8), "89005924");
});

test("TOTP: kellon ero sallitaan, uudelleenkäyttö ei", () => {
  const salaisuus = Buffer.from("12345678901234567890");
  const t = new TotpTarkistin(salaisuus);
  const koodi = totp(salaisuus, 1_000_000);
  assert.equal(t.tarkista(koodi, 1_000_000 + 25), true); // edellinen askel
  assert.equal(t.tarkista(koodi, 1_000_000 + 25), false); // jo käytetty
  assert.equal(t.tarkista(totp(salaisuus, 1_000_000 - 90), 1_000_000),
               false);                                    // liian vanha
});
// @loppu testi
