/** Pankkitili, jonka saldo ei voi mennä negatiiviseksi. */
class Tili {
  static #seuraavaNumero = 1;

  /** Saldo sentteinä; vain luokan omat metodit näkevät kentän. */
  #saldo = 0;
  /** @type {string[]} */
  #tapahtumat = [];

  /**
   * @param {string} omistaja
   */
  constructor(omistaja) {
    if (omistaja.trim() === "") throw new RangeError("omistaja puuttuu");
    this.omistaja = omistaja;
    this.numero = `FI-${String(Tili.#seuraavaNumero++).padStart(4, "0")}`;
  }

  /**
   * Tehdasmetodi: avaa tilin ja tekee alkutalletuksen.
   * @param {string} omistaja
   * @param {number} sentit
   */
  static avaa(omistaja, sentit) {
    const tili = new Tili(omistaja);
    tili.talleta(sentit);
    return tili;
  }

  get saldo() {
    return this.#saldo;
  }

  /** @param {number} sentit */
  talleta(sentit) {
    this.#tarkista(sentit);
    this.#saldo += sentit;
    this.#tapahtumat.push(`+${sentit}`);
    return this;
  }

  /** @param {number} sentit */
  nosta(sentit) {
    this.#tarkista(sentit);
    if (sentit > this.#saldo) {
      throw new RangeError(`kate ei riitä: ${this.#saldo} < ${sentit}`);
    }
    this.#saldo -= sentit;
    this.#tapahtumat.push(`-${sentit}`);
    return this;
  }

  /** @param {number} sentit */
  #tarkista(sentit) {
    if (!Number.isSafeInteger(sentit) || sentit <= 0) {
      throw new RangeError(`virheellinen summa: ${sentit}`);
    }
  }

  toString() {
    return `${this.numero} ${this.omistaja}: ${this.#saldo} snt ` +
      `[${this.#tapahtumat.join(" ")}]`;
  }
}

const tili = Tili.avaa("Aino", 10000).nosta(2550).talleta(500);
console.log(String(tili), tili.saldo);
try {
  tili.nosta(1e6);
} catch (virhe) {
  console.log(virhe instanceof RangeError, String(virhe));
}
console.log(Object.keys(tili), String(new Tili("Eero")));
