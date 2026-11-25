import { Yhteys } from "./yhteys.js";

/** @param {string} kysely */
export function raportti(kysely) {
  using yhteys = new Yhteys("varasto");
  return yhteys.kysy(kysely);
}   // yhteys suljetaan tässä: paluussa ja virheessä
