// Tehtävälistan liiketoimintalogiikka. Tämä moduuli ei tiedä mitään
// käyttöliittymäkehyksistä: samat funktiot palvelevat kaikkia viittä
// toteutusta, ja ne testataan ilman selainta (logiikka.test.ts).

// @alku tyypit
export type Kiire = "tavallinen" | "kiireellinen";
export type Suodatin = "kaikki" | "avoimet" | "valmiit";
export type Lataus = "ladataan" | "virhe" | "valmis";

export interface Tehtava {
  readonly id: number;
  readonly nimi: string;
  readonly kiire: Kiire;
  readonly valmis: boolean;
}
// @loppu tyypit

export const SUODATTIMET: readonly { arvo: Suodatin; nimi: string }[] = [
  { arvo: "kaikki", nimi: "Kaikki" },
  { arvo: "avoimet", nimi: "Avoimet" },
  { arvo: "valmiit", nimi: "Valmiit" },
];

// @alku muutokset
// Muutokset palauttavat uuden taulukon eivätkä muuta vanhaa. Näin sama
// koodi sopii sekä kehyksille, jotka vertaavat viittauksia (React), että
// niille, jotka seuraavat sijoituksia (Vue, Angular, Svelte).
export function lisaa(tehtavat: readonly Tehtava[], nimi: string,
                      kiire: Kiire): Tehtava[] {
  const id = Math.max(0, ...tehtavat.map((t) => t.id)) + 1;
  return [...tehtavat, { id, nimi: nimi.trim(), kiire, valmis: false }];
}

export function vaihda(tehtavat: readonly Tehtava[],
                       id: number): Tehtava[] {
  return tehtavat.map((t) => t.id === id ? { ...t, valmis: !t.valmis } : t);
}

export function poista(tehtavat: readonly Tehtava[],
                       id: number): Tehtava[] {
  return tehtavat.filter((t) => t.id !== id);
}

export function poistaValmiit(tehtavat: readonly Tehtava[]): Tehtava[] {
  return tehtavat.filter((t) => !t.valmis);
}
// @loppu muutokset

// @alku johdetut
// Johdettu tieto lasketaan tilasta aina uudelleen; sitä ei tallenneta.
export function suodata(tehtavat: readonly Tehtava[],
                        suodatin: Suodatin): readonly Tehtava[] {
  if (suodatin === "kaikki") return tehtavat;
  return tehtavat.filter((t) => t.valmis === (suodatin === "valmiit"));
}

export function laske(tehtavat: readonly Tehtava[]) {
  const valmiita = tehtavat.filter((t) => t.valmis).length;
  return { avoimia: tehtavat.length - valmiita, valmiita };
}

export function yhteenveto(tehtavat: readonly Tehtava[]): string {
  const { avoimia, valmiita } = laske(tehtavat);
  const avoin = avoimia === 1 ? "1 avoin" : `${avoimia} avointa`;
  const valmis = valmiita === 1 ? "1 valmis" : `${valmiita} valmista`;
  return `${avoin}, ${valmis}`;
}

export function otsikko(tehtavat: readonly Tehtava[]): string {
  return `Tehtävät (${laske(tehtavat).avoimia})`;
}
// @loppu johdetut

// @alku validointi
/** Palauttaa virheilmoituksen tai null, jos nimi kelpaa. */
export function validoi(nimi: string,
                        tehtavat: readonly Tehtava[]): string | null {
  const siisti = nimi.trim();
  if (siisti.length < 3) return "Nimessä on oltava vähintään 3 merkkiä.";
  if (siisti.length > 40) return "Nimessä saa olla enintään 40 merkkiä.";
  const sama = (t: Tehtava) =>
    t.nimi.toLocaleLowerCase("fi") === siisti.toLocaleLowerCase("fi");
  if (tehtavat.some(sama)) return "Samanniminen tehtävä on jo listalla.";
  return null;
}
// @loppu validointi

// @alku tallennus
const AVAIN = "tehtavat";

function onTehtava(x: unknown): x is Tehtava {
  if (typeof x !== "object" || x === null) return false;
  const t = x as Record<string, unknown>;
  return typeof t.id === "number" && typeof t.nimi === "string" &&
    (t.kiire === "tavallinen" || t.kiire === "kiireellinen") &&
    typeof t.valmis === "boolean";
}

function jasenna(teksti: string): Tehtava[] {
  const data: unknown = JSON.parse(teksti);
  if (!Array.isArray(data) || !data.every(onTehtava)) {
    throw new Error("tehtävälista on väärän muotoinen");
  }
  return data;
}

type Varasto = Pick<Storage, "getItem" | "setItem">;

export function tallenna(varasto: Varasto,
                         tehtavat: readonly Tehtava[]): void {
  varasto.setItem(AVAIN, JSON.stringify(tehtavat));
}

/** Aiemmin tallennettu lista tai null, jos sitä ei ole tai se on rikki. */
export function lueTallennetut(varasto: Varasto): Tehtava[] | null {
  const teksti = varasto.getItem(AVAIN);
  if (teksti === null) return null;
  try { return jasenna(teksti); } catch { return null; }
}

/** Alkutila: selaimeen tallennettu lista tai palvelimen oletuslista. */
export async function haeTehtavat(
  varasto: Varasto, hae: typeof fetch = fetch,
): Promise<Tehtava[]> {
  const tallennetut = lueTallennetut(varasto);
  if (tallennetut !== null) return tallennetut;
  const vastaus = await hae("tehtavat.json");
  if (!vastaus.ok) throw new Error(`HTTP ${vastaus.status}`);
  return jasenna(await vastaus.text());
}
// @loppu tallennus
