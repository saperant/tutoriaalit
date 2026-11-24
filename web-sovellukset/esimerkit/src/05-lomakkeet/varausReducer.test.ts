import { describe, expect, test } from "vitest";
import type { Luonnos } from "./varaus.ts";
import { type LomakeTila, varausReducer } from "./varausReducer.ts";

const LUONNOS: Luonnos = {
  tilaId: "kivi", paiva: "2026-12-01", alku: "09:00", kesto: 60,
  aihe: "Sprintin suunnittelu",
};
const alku: LomakeTila = { vaihe: "muokkaus", luonnos: LUONNOS, virheet: {} };

// @alku testi
describe("varausReducer", () => {
  test("virheellinen luonnos jää muokkaukseen virheineen", () => {
    const tila = varausReducer(
      varausReducer(alku, { tyyppi: "muuta", kentta: "kesto", arvo: "5" }),
      { tyyppi: "laheta", tanaan: "2026-11-24" });
    expect(tila).toMatchObject({
      vaihe: "muokkaus",
      virheet: { kesto: "Keston on oltava 15–480 minuuttia." },
    });
  });

  test("lähetys, epäonnistuminen ja uusi yritys", () => {
    const laheta = { tyyppi: "laheta", tanaan: "2026-11-24" } as const;
    let tila = varausReducer(alku, laheta);
    expect(tila.vaihe).toBe("lahetys");
    tila = varausReducer(tila, { tyyppi: "epaonnistui", viesti: "Varattu" });
    expect(tila).toMatchObject({ vaihe: "virhe", luonnos: LUONNOS });
    tila = varausReducer(tila, laheta);
    tila = varausReducer(tila, { tyyppi: "onnistui", varausId: "v1" });
    expect(tila).toEqual({ vaihe: "valmis", varausId: "v1" });
  });

  test("myöhästynyt vastaus ei muuta valmista tilaa", () => {
    const valmis: LomakeTila = { vaihe: "valmis", varausId: "v1" };
    expect(varausReducer(valmis, { tyyppi: "epaonnistui", viesti: "x" }))
      .toBe(valmis);
  });
});
// @loppu testi
