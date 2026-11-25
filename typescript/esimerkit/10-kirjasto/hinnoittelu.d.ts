// Esittelytiedosto: pelkät tyypit, ei toteutusta.

/** Yleinen arvonlisäverokanta kertoimena (0.255 = 25,5 %). */
export declare const ALV: number;

/**
 * Laskee verollisen hinnan pyöristettynä senttiin.
 *
 * @param hinta - veroton hinta euroina
 * @param alv - verokanta kertoimena; oletus on {@link ALV}
 * @returns verollinen hinta euroina
 * @example
 * verollinen(10);        // 12.55
 * verollinen(10, 0.14);  // 11.4
 */
export declare function verollinen(hinta: number, alv?: number): number;

export interface Alennusehdot {
  /** Alennus prosentteina (0–100). */
  prosentti?: number;
  /** Alennuksen enimmäismäärä euroina. */
  enintaan?: number;
}

/**
 * Vähentää hinnasta alennuksen ehtojen mukaan.
 *
 * @remarks Tulos ei ole koskaan negatiivinen.
 * @param hinta - hinta euroina ennen alennusta
 * @param ehdot - puuttuva kenttä tarkoittaa "ei alennusta" tai
 *   "ei ylärajaa"
 */
export declare function alennus(hinta: number, ehdot?: Alennusehdot):
  number;
