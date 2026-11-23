/**
 * LRU-välimuisti: Map säilyttää lisäysjärjestyksen, joten vanhin avain
 * on iteroinnissa ensimmäisenä. Koko on rajattu, jotta muisti ei kasva
 * rajatta (yleisin Node-palvelimen muistivuoto on rajaton välimuisti).
 * @template K, V
 */
export class LruValimuisti {
  /** @type {Map<K, V>} */
  #data = new Map();
  #koko;

  /** @param {number} koko */
  constructor(koko) {
    if (!Number.isInteger(koko) || koko < 1) {
      throw new RangeError(`koko ei kelpaa: ${koko}`);
    }
    this.#koko = koko;
  }

  /**
   * @param {K} avain
   * @returns {V | undefined}
   */
  hae(avain) {
    if (!this.#data.has(avain)) return undefined;
    const arvo = /** @type {V} */ (this.#data.get(avain));
    this.#data.delete(avain);     // siirretään tuoreimmaksi
    this.#data.set(avain, arvo);
    return arvo;
  }

  /**
   * @param {K} avain
   * @param {V} arvo
   */
  aseta(avain, arvo) {
    this.#data.delete(avain);
    this.#data.set(avain, arvo);
    if (this.#data.size > this.#koko) {
      const vanhin = this.#data.keys().next().value;
      this.#data.delete(/** @type {K} */ (vanhin));
    }
  }

  get avaimet() {
    return [...this.#data.keys()];
  }
}

/** @type {LruValimuisti<string, number>} */
const hinnat = new LruValimuisti(2);
hinnat.aseta("kahvi", 650);
hinnat.aseta("tee", 425);
hinnat.hae("kahvi");
hinnat.aseta("mehu", 300);          // tee poistuu
console.log(hinnat.avaimet, hinnat.hae("tee"));
