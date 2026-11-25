import { test } from "node:test";
import assert from "node:assert/strict";
import { Palautus } from "./palautus.ts";

// @alku testi
test("palautus: kertakäyttöinen, vanheneva, uusi mitätöi vanhan", () => {
  let nyt = 0;
  const p = new Palautus(["aino"], () => nyt);
  assert.equal(p.pyyda("tuntematon"), undefined);

  const token = p.pyyda("aino")!;
  assert.equal(Buffer.from(token, "base64url").length, 32);
  assert.equal(p.kayta("arvaus"), undefined);
  assert.equal(p.kayta(token), "aino");
  assert.equal(p.kayta(token), undefined);       // jo käytetty

  const vanha = p.pyyda("aino")!;
  const uusi = p.pyyda("aino")!;
  assert.equal(p.kayta(vanha), undefined);       // uusi pyyntö mitätöi
  nyt += 31 * 60_000;
  assert.equal(p.kayta(uusi), undefined);        // vanhentunut
});
// @loppu testi
