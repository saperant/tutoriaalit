// catch-muuttuja on unknown: heitetty arvo voi olla mitä tahansa.
class TilausVirhe extends Error {
  override readonly name = "TilausVirhe";
  readonly tilausId: string;
  constructor(tilausId: string, viesti: string, options?: ErrorOptions) {
    super(viesti, options);
    this.tilausId = tilausId;
  }
}

function lueMaara(teksti: string): number {
  const n = Number(teksti);
  if (!Number.isInteger(n)) {
    throw new RangeError(`ei kokonaisluku: ${teksti}`);
  }
  return n;
}

function kasittele(tilausId: string, maara: string): number {
  try {
    return lueMaara(maara);
  } catch (e) {
    // Ketjutus: alkuperäinen syy säilyy cause-kentässä.
    throw new TilausVirhe(tilausId, "määrä virheellinen", { cause: e });
  }
}

function viesti(e: unknown): string {
  if (e instanceof TilausVirhe) {
    const syy = e.cause instanceof Error ? e.cause.message : "?";
    return `${e.name} ${e.tilausId}: ${e.message} (${syy})`;
  }
  if (e instanceof Error) return e.message;
  return String(e); // throw "teksti" on sallittu, mutta huono tapa
}

for (const [id, maara] of [["T1", "3"], ["T2", "kolme"]] as const) {
  try {
    console.log(id, kasittele(id, maara));
  } catch (e) {
    console.log(viesti(e));
  }
}
try {
  throw "merkkijono";
} catch (e) {
  console.log(viesti(e));
}
