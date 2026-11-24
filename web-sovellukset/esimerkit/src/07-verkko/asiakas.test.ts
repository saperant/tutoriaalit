// @vitest-environment node
import { afterAll, beforeAll, describe, expect, test } from "vitest";
import { kaynnista } from "../../palvelin/api.ts";
import { ApiVirhe, luoAsiakas } from "./asiakas.ts";
import { JasennysVirhe } from "./skeema.ts";

// @alku integraatio
describe("API-asiakas oikeaa HTTP-palvelinta vasten", () => {
  let palvelin: Awaited<ReturnType<typeof kaynnista>>;
  beforeAll(async () => { palvelin = await kaynnista(); });
  afterAll(() => palvelin.sulje());

  const luonnos = { tilaId: "kivi", paiva: "2026-12-01", alku: "09:00",
                    kesto: 60, aihe: "Retro" };

  test("tilat jäsennetään tyypitetyiksi", async () => {
    const tilat = await luoAsiakas(palvelin.osoite).haeTilat();
    expect(tilat.map((t) => t.id)).toEqual(["aalto", "kivi", "sibelius",
                                             "tove"]);
  });

  test("päällekkäinen varaus on 409, jota ei kannata yrittää uudelleen",
    async () => {
      const api = luoAsiakas(palvelin.osoite);
      expect(await api.varaa(luonnos)).toBe("v1");
      const virhe = await api.varaa(luonnos).catch((e: unknown) => e);
      expect(virhe).toBeInstanceOf(ApiVirhe);
      expect(virhe).toMatchObject({ status: 409,
        message: "Tila on jo varattu.", uudelleenyritettava: false });
    });
});
// @loppu integraatio

// @alku jasennys
test("odottamaton vastaus pysähtyy rajapinnan reunalle", async () => {
  const valeFetch = async () => Response.json([{ id: "x", nimi: 7 }]);
  const api = luoAsiakas("", valeFetch);
  await expect(api.haeTilat()).rejects.toThrow(
    new JasennysVirhe("tilat[0].nimi: ei tekstiä"));
});
// @loppu jasennys
