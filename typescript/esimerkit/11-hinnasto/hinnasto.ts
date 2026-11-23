// Testattava moduli: puhtaita funktioita ilman sivuvaikutuksia.
export type Hintasaanto =
  | { laji: "kiintea"; sentit: number }
  | { laji: "maara"; rajat: readonly { alkaen: number; sentit: number }[] };

/** Yksikköhinta sentteinä tilattavalle määrälle. */
export function yksikkohinta(s: Hintasaanto, maara: number): number {
  if (!Number.isInteger(maara) || maara <= 0) {
    throw new RangeError(`virheellinen määrä: ${maara}`);
  }
  if (s.laji === "kiintea") return s.sentit;
  // Suurin raja, joka ei ylitä määrää; rajat nousevassa järjestyksessä.
  const sopivat = s.rajat.filter((r) => r.alkaen <= maara);
  const raja = sopivat.at(-1);
  if (raja === undefined) throw new RangeError("ei hintaa määrälle");
  return raja.sentit;
}

export function rivihinta(s: Hintasaanto, maara: number): number {
  return yksikkohinta(s, maara) * maara;
}
