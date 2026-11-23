import { setTimeout as odota } from "node:timers/promises";

/**
 * Simuloitu verkkopalvelu: vastaa viiveen jälkeen tai epäonnistuu.
 * @param {string} tuote
 * @param {number} viive  millisekunteina
 * @returns {Promise<number>}
 */
async function haeHinta(tuote, viive) {
  await odota(viive);
  if (tuote === "mehu") throw new Error(`${tuote}: palvelu ei vastaa`);
  return tuote.length * 100;
}

// @alku perakkain
const alku1 = performance.now();
for (const tuote of ["kahvi", "tee", "leipä"]) {
  await haeHinta(tuote, 60);   // odotetaan jokaista vuorollaan
}
const perakkain = performance.now() - alku1;

const alku2 = performance.now();
await Promise.all(["kahvi", "tee", "leipä"].map((t) => haeHinta(t, 60)));
const rinnakkain = performance.now() - alku2;
console.log(`peräkkäin ≥ 180 ms: ${perakkain >= 175}`);
console.log(`rinnakkain < 150 ms: ${rinnakkain < 150}`);
// @loppu perakkain

// @alku yhdistimet
const tuotteet = ["kahvi", "mehu", "tee"];
try {
  await Promise.all(tuotteet.map((t) => haeHinta(t, 10)));
} catch (virhe) {
  console.log("all:", virhe instanceof Error && virhe.message);
}

const tulokset = await Promise.allSettled(
  tuotteet.map((t) => haeHinta(t, 10)),
);
for (const [i, t] of tulokset.entries()) {
  console.log(tuotteet[i], t.status === "fulfilled" ? t.value : "virhe");
}

const nopein = await Promise.race([
  haeHinta("hidas", 100),
  haeHinta("nopea", 10),
]);
console.log("race:", nopein);
// @loppu yhdistimet
