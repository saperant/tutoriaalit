// Geneeriset funktiot ja luokat, rajoitteet ja keyof.
function ensimmainen<T>(xs: readonly T[]): T | undefined {
  return xs[0];
}

// Rajoite: T:llä on oltava id. Paluutyyppi säilyttää koko T:n.
function indeksoi<T extends { id: string }>(xs: readonly T[]):
    Map<string, T> {
  return new Map(xs.map((x) => [x.id, x]));
}

// keyof: avain on rajattu T:n kenttiin, ja arvon tyyppi seuraa avainta.
function poimi<T, K extends keyof T>(x: T, ...avaimet: K[]): Pick<T, K> {
  const tulos = {} as Pick<T, K>; // rakennetaan kenttä kerrallaan
  for (const k of avaimet) tulos[k] = x[k];
  return tulos;
}

// Geneerinen luokka oletustyyppiparametrilla.
class Valimuisti<K, V = string> {
  #data = new Map<K, { arvo: V; vanhenee: number }>();
  readonly #ika: number;
  constructor(ikaMs: number) { this.#ika = ikaMs; }
  aseta(k: K, arvo: V, nyt: number): void {
    this.#data.set(k, { arvo, vanhenee: nyt + this.#ika });
  }
  hae(k: K, nyt: number): V | undefined {
    const m = this.#data.get(k);
    return m && m.vanhenee > nyt ? m.arvo : undefined;
  }
}

const tuotteet = [
  { id: "p1", nimi: "omena", hinta: 0.45, varastossa: true },
  { id: "p2", nimi: "leipä", hinta: 2.9, varastossa: false },
];
console.log(ensimmainen(tuotteet)?.nimi, ensimmainen([])); // T = never
const hakemisto = indeksoi(tuotteet);
console.log(hakemisto.get("p2")?.hinta);
console.log(poimi(tuotteet[1]!, "nimi", "varastossa"));

const muisti = new Valimuisti<number>(1000); // V = string
muisti.aseta(1, "omena", 0);
console.log(muisti.hae(1, 500), muisti.hae(1, 1500));
