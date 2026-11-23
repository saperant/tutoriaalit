// Varastokirjanpidon moduli. Vain export-merkityt nimet näkyvät ulos;
// muu tila on modulin yksityistä.

/** @typedef {{ tuote: string, maara: number }} Saldo */

/** Saldo, jonka alittuessa tuote tilataan lisää. */
export const TILAUSRAJA = 5;

/**
 * Luo uuden varaston. Tehdasfunktio palauttaa rajapinnan, jonka takana
 * tietorakenne on piilossa.
 * @param {Iterable<[string, number]>} [alku]
 */
export function luoVarasto(alku = []) {
  /** @type {Map<string, number>} */
  const saldot = new Map(alku);

  return {
    /**
     * @param {string} tuote
     * @param {number} muutos  positiivinen = saapuminen
     */
    kirjaa(tuote, muutos) {
      if (!Number.isInteger(muutos) || muutos === 0) {
        throw new RangeError(`virheellinen muutos: ${muutos}`);
      }
      const uusi = (saldot.get(tuote) ?? 0) + muutos;
      if (uusi < 0) throw new RangeError(`${tuote}: saldo ei riitä`);
      saldot.set(tuote, uusi);
    },

    /** @returns {Saldo[]} */
    tilattavat() {
      return [...saldot]
        .filter(([, maara]) => maara < TILAUSRAJA)
        .map(([tuote, maara]) => ({ tuote, maara }));
    },

    /** @param {string} tuote */
    saldo(tuote) {
      return saldot.get(tuote) ?? 0;
    },
  };
}

/** @typedef {ReturnType<typeof luoVarasto>} Varasto */
