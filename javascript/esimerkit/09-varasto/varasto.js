// Varastokirjanpidon moduli. Vain export-merkityt nimet näkyvät ulos;
// muu tila on modulin yksityistä.

/** @typedef {{ tuote: string, maara: number }} Saldo */

/** Saldo, jonka alittuessa tuote tilataan lisää. */
export const TILAUSRAJA = 5;

/**
 * Luo uuden varaston.
 *
 * Tehdasfunktio palauttaa rajapinnan, jonka takana tietorakenne on
 * piilossa. Saldot ovat kokonaislukuja eivätkä voi olla negatiivisia.
 *
 * @param {Iterable<[string, number]>} [alku] alkusaldot pareina
 * @example
 * const varasto = luoVarasto([["kahvi", 3]]);
 * varasto.kirjaa("kahvi", -1);
 * varasto.saldo("kahvi");   // 2
 */
export function luoVarasto(alku = []) {
  /** @type {Map<string, number>} */
  const saldot = new Map(alku);

  return {
    /**
     * Kirjaa saapumisen tai oton.
     * @param {string} tuote
     * @param {number} muutos  positiivinen = saapuminen
     * @throws {RangeError} jos muutos ei ole nollasta poikkeava
     *   kokonaisluku tai saldo jäisi negatiiviseksi
     */
    kirjaa(tuote, muutos) {
      if (!Number.isInteger(muutos) || muutos === 0) {
        throw new RangeError(`virheellinen muutos: ${muutos}`);
      }
      const uusi = (saldot.get(tuote) ?? 0) + muutos;
      if (uusi < 0) throw new RangeError(`${tuote}: saldo ei riitä`);
      saldot.set(tuote, uusi);
    },

    /**
     * Tuotteet, joiden saldo on alle rajan {@link TILAUSRAJA}.
     * @returns {Saldo[]}
     */
    tilattavat() {
      return [...saldot]
        .filter(([, maara]) => maara < TILAUSRAJA)
        .map(([tuote, maara]) => ({ tuote, maara }));
    },

    /**
     * Tuotteen saldo; tuntemattoman tuotteen saldo on 0.
     * @param {string} tuote
     */
    saldo(tuote) {
      return saldot.get(tuote) ?? 0;
    },
  };
}

/** @typedef {ReturnType<typeof luoVarasto>} Varasto */
