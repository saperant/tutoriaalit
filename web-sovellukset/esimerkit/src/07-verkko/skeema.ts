import type { Tila } from "../tilat.ts";

// Ajonaikainen jäsennys rajapinnan reunalla (parse, don't validate):
// palvelimen vastaus on unknown, kunnes se on tarkistettu. Tuotannossa
// tähän käytetään usein kirjastoa (esim. Zod tai Valibot).

export class JasennysVirhe extends Error {}

// @alku skeema
function olio(x: unknown, polku: string): Record<string, unknown> {
  if (typeof x !== "object" || x === null || Array.isArray(x)) {
    throw new JasennysVirhe(`${polku}: odotettiin oliota`);
  }
  return x as Record<string, unknown>;
}
function teksti(x: unknown, polku: string): string {
  if (typeof x !== "string") throw new JasennysVirhe(`${polku}: ei tekstiä`);
  return x;
}
function kokonaisluku(x: unknown, polku: string): number {
  if (!Number.isInteger(x)) throw new JasennysVirhe(`${polku}: ei lukua`);
  return x as number;
}
function lista<T>(x: unknown, polku: string,
                  alkio: (y: unknown, p: string) => T): T[] {
  if (!Array.isArray(x)) throw new JasennysVirhe(`${polku}: ei lista`);
  return x.map((y, i) => alkio(y, `${polku}[${i}]`));
}

export function jasennaTila(x: unknown, polku = "tila"): Tila {
  const o = olio(x, polku);
  return {
    id: teksti(o.id, `${polku}.id`),
    nimi: teksti(o.nimi, `${polku}.nimi`),
    kerros: kokonaisluku(o.kerros, `${polku}.kerros`),
    paikkoja: kokonaisluku(o.paikkoja, `${polku}.paikkoja`),
    varusteet: lista(o.varusteet, `${polku}.varusteet`, teksti),
  };
}

export const jasennaTilat = (x: unknown) => lista(x, "tilat", jasennaTila);

export function jasennaVarausId(x: unknown): string {
  return teksti(olio(x, "vastaus").id, "vastaus.id");
}
// @loppu skeema
