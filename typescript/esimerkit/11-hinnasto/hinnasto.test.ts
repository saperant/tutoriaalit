// Ajetaan: node --test (Node poistaa tyypit myös testitiedostoista).
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { rivihinta, yksikkohinta, type Hintasaanto } from "./hinnasto.ts";

const porrastettu: Hintasaanto = {
  laji: "maara",
  rajat: [{ alkaen: 1, sentit: 100 }, { alkaen: 10, sentit: 80 }],
};

describe("yksikkohinta", () => {
  it("käyttää kiinteää hintaa", () => {
    assert.equal(yksikkohinta({ laji: "kiintea", sentit: 45 }, 3), 45);
  });

  // Taulukkotesti: tapaukset datana, raja-arvot mukana.
  const tapaukset = [[1, 100], [9, 100], [10, 80], [500, 80]] as const;
  for (const [maara, odotettu] of tapaukset) {
    it(`porrastus määrälle ${maara}`, () => {
      assert.equal(yksikkohinta(porrastettu, maara), odotettu);
    });
  }

  it("hylkää virheellisen määrän", () => {
    for (const m of [0, -1, 1.5, Number.NaN]) {
      assert.throws(() => yksikkohinta(porrastettu, m), RangeError);
    }
  });
});

describe("rivihinta", () => {
  it("kertoo yksikköhinnan määrällä", () => {
    assert.equal(rivihinta(porrastettu, 12), 960);
  });
});
