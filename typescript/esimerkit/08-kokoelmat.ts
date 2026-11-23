// Kokoelmat tyypitettyinä: taulukot, monikot, Map, Set ja ryhmittely.
type Myynti = { tuote: string; alue: "etelä" | "pohjoinen"; euroa: number };

const myynnit: readonly Myynti[] = [
  { tuote: "omena", alue: "etelä", euroa: 120 },
  { tuote: "leipä", alue: "pohjoinen", euroa: 80 },
  { tuote: "omena", alue: "pohjoinen", euroa: 45 },
  { tuote: "maito", alue: "etelä", euroa: 60 },
];
// myynnit.push(...) olisi virhe: readonly-taulukossa ei ole push-metodia.

// Object.groupBy (ES2024): avaimet literaaliunionista.
const alueittain = Object.groupBy(myynnit, (m) => m.alue);
const etela = alueittain.etelä ?? []; // ryhmä voi puuttua
console.log(etela.map((m) => m.tuote));

// Map, kun avaimet ovat dataa eivätkä kiinteitä kenttiä.
const tuotteittain = new Map<string, number>();
for (const { tuote, euroa } of myynnit) {
  tuotteittain.set(tuote, (tuotteittain.get(tuote) ?? 0) + euroa);
}
const jarjestetty = [...tuotteittain].sort(([, a], [, b]) => b - a);
console.log(jarjestetty); // [string, number][]

// Set ja toSorted (ei muuta alkuperäistä).
const tuotteet = new Set(myynnit.map((m) => m.tuote));
console.log([...tuotteet].toSorted());

// Monikon palautus: nimetyt paikat dokumentoivat merkityksen.
function minMax(xs: readonly number[]): [min: number, max: number] {
  return [Math.min(...xs), Math.max(...xs)];
}
const [pienin, suurin] = minMax(myynnit.map((m) => m.euroa));
console.log(pienin, suurin);
