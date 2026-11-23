// Laskee syötteen yleisimmät sanat.
// Käyttö: node 01-sanalaskuri.js < teksti.txt
import { text } from "node:stream/consumers";

const NAYTETTAVIA = 5;

/**
 * Pilkkoo tekstin pieniksi kirjoitetuiksi sanoiksi.
 * @param {string} teksti
 * @returns {string[]}
 */
function sanat(teksti) {
  return teksti.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [];
}

/**
 * Laskee kunkin sanan esiintymät.
 * @param {Iterable<string>} lista
 * @returns {Map<string, number>}
 */
function laske(lista) {
  const maarat = new Map();
  for (const sana of lista) {
    maarat.set(sana, (maarat.get(sana) ?? 0) + 1);
  }
  return maarat;
}

const maarat = laske(sanat(await text(process.stdin)));
const yleisimmat = [...maarat]
  .sort(([a, m], [b, n]) => n - m || a.localeCompare(b, "fi"))
  .slice(0, NAYTETTAVIA);

for (const [sana, maara] of yleisimmat) {
  console.log(`${String(maara).padStart(3)}  ${sana}`);
}
