// Apuvälinetyypit johtavat uusia tyyppejä yhdestä mallista.
type Tuote = {
  id: string;
  nimi: string;
  hinta: number;
  kuvaus?: string;
};

type UusiTuote = Omit<Tuote, "id">; // luotaessa id:tä ei vielä ole
type Muutos = Partial<Omit<Tuote, "id">>; // kaikki kentät valinnaisia
type Esikatselu = Pick<Tuote, "nimi" | "hinta">;
type Taydellinen = Required<Tuote>; // kuvaus pakollinen
type Hinnasto = Record<Tuote["id"], number>; // indeksoitu tyyppi

let seuraava = 1;
function luo(t: UusiTuote): Tuote {
  return { id: `p${seuraava++}`, ...t };
}
function paivita(t: Readonly<Tuote>, m: Muutos): Tuote {
  return { ...t, ...m }; // uusi olio; alkuperäinen ei muutu
}

const omena = luo({ nimi: "omena", hinta: 0.45 });
const kallis = paivita(omena, { hinta: 0.55 });
const e: Esikatselu = kallis; // ylimääräiset kentät sallittuja
const t: Taydellinen = { ...kallis, kuvaus: kallis.kuvaus ?? "" };
const h: Hinnasto = { [t.id]: t.hinta };
console.log(omena.hinta, kallis.hinta, e.nimi, JSON.stringify(h));

// Funktioiden tyypeistä: ReturnType, Parameters, Awaited.
async function hae(id: string, tuore = false): Promise<Tuote> {
  return { id, nimi: tuore ? "tuore" : "vanha", hinta: 1 };
}
type HaunParametrit = Parameters<typeof hae>; // [id: string, tuore?: ...]
type Haettu = Awaited<ReturnType<typeof hae>>; // Tuote
const p: HaunParametrit = ["p9"];
const x: Haettu = await hae(...p);
console.log(x.nimi, x.id);
