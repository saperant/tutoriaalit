import { setTimeout as odota } from "node:timers/promises";

// @alku rajoitin
/**
 * Ajaa tehtävät niin, että enintään `raja` on käynnissä kerralla.
 * Tulokset palautetaan syötteen järjestyksessä.
 * @template T, R
 * @param {readonly T[]} syotteet
 * @param {number} raja
 * @param {(syote: T) => Promise<R>} tehtava
 * @returns {Promise<R[]>}
 */
async function rajoitettu(syotteet, raja, tehtava) {
  /** @type {R[]} */
  const tulokset = new Array(syotteet.length);
  let seuraava = 0;

  async function tyontekija() {
    while (seuraava < syotteet.length) {
      // Ei kilpailutilannetta: JS-koodi ajetaan yhdessä säikeessä, ja
      // vuoro vaihtuu vain await-kohdassa.
      const i = seuraava++;
      tulokset[i] = await tehtava(syotteet[i]);
    }
  }

  const maara = Math.min(raja, syotteet.length);
  await Promise.all(Array.from({ length: maara }, tyontekija));
  return tulokset;
}
// @loppu rajoitin

// @alku kaytto
let kaynnissa = 0;
let enimmillaan = 0;

/** @param {number} n */
async function lataa(n) {
  kaynnissa += 1;
  enimmillaan = Math.max(enimmillaan, kaynnissa);
  await odota(5 + (n % 3) * 5);
  kaynnissa -= 1;
  return `sivu-${n}`;
}

const sivut = Array.from({ length: 10 }, (_, i) => i + 1);
const tulos = await rajoitettu(sivut, 3, lataa);
console.log(tulos.join(" "));
console.log(`enimmillään rinnakkain: ${enimmillaan}`);
// @loppu kaytto
