import { Yhteys } from "./yhteys.js";

/** @param {string} kysely */
export function raportti(kysely) {
  const yhteys = new Yhteys("varasto");
  try {
    return yhteys.kysy(kysely);
  } finally {
    yhteys[Symbol.dispose]();   // ajetaan paluussa ja virheessä
  }
}
