// Pikaoppaan koodi: jokainen osa tarkistetaan ja ajetaan.
// @alku tyypit
type Id = string;
type Tila = "auki" | "kiinni"; // literaaliunioni
type Piste = readonly [x: number, y: number]; // monikko
interface Tuote { readonly id: Id; nimi: string; hinta?: number }
type Hinnoiteltu = Tuote & { hinta: number }; // leikkaus
const vakiot = { alv: 0.255, valuutta: "EUR" } as const;
let tuntematon: unknown = JSON.parse("1"); // ei any:ä
// @loppu tyypit

// @alku unionit
type Tulos<T> = { ok: true; arvo: T } | { ok: false; virhe: string };
function arvo<T>(t: Tulos<T>, oletus: T): T {
  return t.ok ? t.arvo : oletus; // kavennus erottimella ok
}
function eiKasitelty(x: never): never {
  throw new Error(`käsittelemätön: ${String(x)}`);
}
function nimi(t: Tila): string {
  switch (t) {
    case "auki": return "avoinna";
    case "kiinni": return "suljettu";
    default: return eiKasitelty(t); // kattavuustarkistus
  }
}
// @loppu unionit

// @alku vartijat
function onTuote(x: unknown): x is Tuote {
  return typeof x === "object" && x !== null && "id" in x
    && typeof x.id === "string" && "nimi" in x
    && typeof x.nimi === "string";
}
function varmista(ehto: unknown, viesti: string): asserts ehto {
  if (!ehto) throw new Error(viesti);
}
// @loppu vartijat

// @alku geneeriset
function poimi<T, K extends keyof T>(x: T, k: K): T[K] {
  return x[k];
}
type Muutos = Partial<Omit<Tuote, "id">>;
type Tyyppi<J> = J extends (x: unknown) => infer T ? T : never;
const asetukset = {
  sivukoko: 20, kieli: "fi",
} satisfies Record<string, string | number>;
// @loppu geneeriset

const p: Piste = [1, 2];
const h: Hinnoiteltu = { id: "p1", nimi: "omena", hinta: 0.45 };
const m: Muutos = { nimi: "vihreä omena" };
const tyyppi: Tyyppi<(x: unknown) => number> = 3;
varmista(onTuote(h), "ei tuote");
tuntematon = poimi(h, "nimi");
console.log(arvo({ ok: false, virhe: "x" }, 0), nimi("auki"), p[1],
  m.nimi, tyyppi, tuntematon, vakiot.alv, asetukset.sivukoko);
