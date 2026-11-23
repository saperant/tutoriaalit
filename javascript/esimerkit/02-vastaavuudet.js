// @alku tietue
/** @typedef {{ nimi: string, hinta: number, tagit: string[] }} Tuote */

/** @type {Tuote[]} */
const tuotteet = [
  { nimi: "kahvi", hinta: 6.5, tagit: ["juoma", "luomu"] },
  { nimi: "tee", hinta: 4.2, tagit: ["juoma"] },
  { nimi: "leipä", hinta: 3.1, tagit: ["leivonnainen", "luomu"] },
];

// Purkaminen (destructuring) ja levitys (spread).
const [ensimmainen, ...muut] = tuotteet;
const { nimi, hinta } = ensimmainen;
const alennettu = { ...ensimmainen, hinta: hinta * 0.9 };
console.log(nimi, muut.length, alennettu.hinta.toFixed(2));
// @loppu tietue

// @alku kokoelmat
const luomu = tuotteet
  .filter((t) => t.tagit.includes("luomu"))
  .map((t) => t.nimi);
const hinnat = new Map(tuotteet.map((t) => [t.nimi, t.hinta]));
const tagit = new Set(tuotteet.flatMap((t) => t.tagit));
console.log(luomu, hinnat.get("tee"), [...tagit].sort());
// @loppu kokoelmat

// @alku async
/**
 * Simuloi verkkokutsua: palauttaa lupauksen, joka täyttyy myöhemmin.
 * @param {string} tuote
 * @returns {Promise<number>}
 */
async function haeVarasto(tuote) {
  await new Promise((valmis) => setTimeout(valmis, 10));
  return tuote.length * 3;
}

const saldot = await Promise.all(tuotteet.map((t) => haeVarasto(t.nimi)));
console.log(saldot);
// @loppu async
