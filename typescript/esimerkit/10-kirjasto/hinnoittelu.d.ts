// Esittelytiedosto: pelkät tyypit, ei toteutusta.
export declare const ALV: number;

/** Verollinen hinta pyöristettynä senttiin. */
export declare function verollinen(hinta: number, alv?: number): number;

export interface Alennusehdot {
  /** Alennus prosentteina (0–100). */
  prosentti?: number;
  /** Alennuksen enimmäismäärä euroina. */
  enintaan?: number;
}
export declare function alennus(hinta: number, ehdot?: Alennusehdot):
  number;
