import assert from "node:assert/strict";
import { describe, it, mock } from "node:test";
import { hinta, valimuistilla } from "./hinnoittelu.js";

/** Testin kurssilähde: kiinteät kurssit ja kutsujen kirjanpito. */
function testilahde() {
  return {
    kurssi: mock.fn(async (/** @type {string} */ valuutta) =>
      valuutta === "SEK" ? 11.5 : Number.NaN),
  };
}

describe("hinta", () => {
  const tapaukset = [
    { sentit: 1000, valuutta: "EUR", odotettu: 1000 },
    { sentit: 1000, valuutta: "SEK", odotettu: 11500 },
    { sentit: 3, valuutta: "SEK", odotettu: 35 },
  ];
  for (const { sentit, valuutta, odotettu } of tapaukset) {
    it(`${sentit} snt -> ${valuutta}`, async () => {
      assert.equal(await hinta({ sentit, valuutta }, testilahde()),
        odotettu);
    });
  }

  it("ei kysy kurssia euroille", async () => {
    const lahde = testilahde();
    await hinta({ sentit: 500, valuutta: "EUR" }, lahde);
    assert.equal(lahde.kurssi.mock.callCount(), 0);
  });

  it("hylkää virheellisen summan ja kurssin", async () => {
    await assert.rejects(hinta({ sentit: -1, valuutta: "EUR" },
      testilahde()), RangeError);
    await assert.rejects(hinta({ sentit: 1, valuutta: "XYZ" },
      testilahde()), /virheellinen kurssi/);
  });
});

describe("valimuistilla", () => {
  it("hakee kurssin uudelleen vasta, kun ikä täyttyy", async () => {
    mock.timers.enable({ apis: ["Date"], now: 0 });
    try {
      const lahde = testilahde();
      const muisti = valimuistilla(lahde, 60_000);
      await muisti.kurssi("SEK");
      mock.timers.tick(59_999);
      await muisti.kurssi("SEK");
      assert.equal(lahde.kurssi.mock.callCount(), 1);
      mock.timers.tick(1);
      await muisti.kurssi("SEK");
      assert.equal(lahde.kurssi.mock.callCount(), 2);
    } finally {
      mock.timers.reset();
    }
  });
});
