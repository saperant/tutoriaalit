/** @typedef {{ tuote: string, ryhma: string, hinta: number }} Rivi */

/** @type {Rivi[]} */
const rivit = [
  { tuote: "tee", ryhma: "juomat", hinta: 425 },
  { tuote: "äyriäiset", ryhma: "kala", hinta: 1290 },
  { tuote: "kahvi", ryhma: "juomat", hinta: 650 },
  { tuote: "lohi", ryhma: "kala", hinta: 1890 },
  { tuote: "Pätkis", ryhma: "leivonnaiset", hinta: 199 },
];

// @alku perus
const kalliit = rivit.filter((r) => r.hinta > 500).map((r) => r.tuote);
const summa = rivit.reduce((s, r) => s + r.hinta, 0);
const halvin = rivit.reduce((a, b) => (b.hinta < a.hinta ? b : a));
console.log(kalliit, summa, halvin.tuote);
console.log(rivit.some((r) => r.hinta > 1500), rivit.at(-1)?.tuote);
console.log(rivit.findLast((r) => r.ryhma === "juomat")?.tuote);
// @loppu perus

// @alku lajittelu
const luvut = [10, 9, 100, 1];
console.log(luvut.toSorted(), luvut.toSorted((a, b) => a - b));
const aakkoset = new Intl.Collator("fi");
console.log(rivit.map((r) => r.tuote).toSorted(aakkoset.compare));
console.log(rivit.map((r) => r.tuote).toSorted()); // UTF-16-järjestys
// sort() muuttaa taulukkoa ja on vakaa: tasatilanteet säilyttävät
// alkuperäisen järjestyksen, joten lajittelut voi ketjuttaa.
const kopio = [...rivit];
kopio.sort((a, b) => a.ryhma.localeCompare(b.ryhma, "fi"));
console.log(kopio.map((r) => r.tuote).join(" "));
// @loppu lajittelu

// @alku ryhmittely
const ryhmat = Object.groupBy(rivit, (r) => r.ryhma);
for (const [ryhma, jasenet = []] of Object.entries(ryhmat)) {
  const yht = jasenet.reduce((s, r) => s + r.hinta, 0);
  console.log(`${ryhma.padEnd(14)}${jasenet.length} kpl ${yht} snt`);
}
// @loppu ryhmittely

// @alku reiat
const harva = [1, , 3];   // reikä indeksissä 1
console.log(harva.length, 1 in harva, harva.map(String));
console.log(Array.from({ length: 3 }, (_, i) => i * i));
// @loppu reiat
