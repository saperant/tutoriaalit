/**
 * @typedef {object} Kurssilahde
 * @property {(valuutta: string) => Promise<number>} kurssi
 *   euron kurssi valuuttaan
 */

/**
 * Laskee tilauksen hinnan valuutassa. Kurssilähde annetaan
 * parametrina (riippuvuuden injektio), joten testi voi korvata sen.
 * @param {{ sentit: number, valuutta: string }} tilaus
 * @param {Kurssilahde} lahde
 * @returns {Promise<number>} hinta valuutan sadasosina
 */
export async function hinta({ sentit, valuutta }, lahde) {
  if (!Number.isSafeInteger(sentit) || sentit < 0) {
    throw new RangeError(`virheellinen summa: ${sentit}`);
  }
  if (valuutta === "EUR") return sentit;
  const kurssi = await lahde.kurssi(valuutta);
  if (!(kurssi > 0)) throw new RangeError(`virheellinen kurssi: ${kurssi}`);
  return Math.round(sentit * kurssi);
}

/**
 * Kurssilähde, joka muistaa kurssit `ika` millisekuntia.
 * @param {Kurssilahde} lahde
 * @param {number} ika
 * @returns {Kurssilahde}
 */
export function valimuistilla(lahde, ika) {
  /** @type {Map<string, { arvo: number, haettu: number }>} */
  const muisti = new Map();
  return {
    async kurssi(valuutta) {
      const tallessa = muisti.get(valuutta);
      if (tallessa && Date.now() - tallessa.haettu < ika) {
        return tallessa.arvo;
      }
      const arvo = await lahde.kurssi(valuutta);
      muisti.set(valuutta, { arvo, haettu: Date.now() });
      return arvo;
    },
  };
}
