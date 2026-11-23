/** @import { Saldo } from "./varasto.js" */

/**
 * @param {Saldo[]} saldot
 * @returns {string}
 */
export default function muotoileTilaus(saldot) {
  if (saldot.length === 0) return "ei tilattavaa";
  return saldot
    .map(({ tuote, maara }) => `${tuote.padEnd(8)}saldo ${maara}`)
    .join("\n");
}
