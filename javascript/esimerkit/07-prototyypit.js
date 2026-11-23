// @alku ketju
const elain = {
  /** @this {{ nimi: string, aani: string }} */
  aantele() {
    return `${this.nimi} sanoo ${this.aani}`;
  },
};
const kissa = Object.create(elain);
kissa.nimi = "Miuku";
kissa.aani = "miau";
console.log(kissa.aantele(), Object.getPrototypeOf(kissa) === elain);
console.log(Object.hasOwn(kissa, "nimi"), Object.hasOwn(kissa, "aantele"));
// @loppu ketju

// @alku luokka
class Muoto {
  /** @param {string} nimi */
  constructor(nimi) {
    this.nimi = nimi;
  }

  pinta() {
    return 0;
  }

  kuvaus() {
    return `${this.nimi}: ${this.pinta().toFixed(2)}`;
  }
}

class Ympyra extends Muoto {
  /** @param {number} r */
  constructor(r) {
    super("ympyrä");
    this.r = r;
  }

  pinta() {
    return Math.PI * this.r ** 2;
  }
}

const y = new Ympyra(1);
console.log(y.kuvaus(), y instanceof Muoto, typeof Ympyra);
// Metodit ovat prototyypissä, kentät oliossa itsessään:
console.log(Object.keys(y), Object.hasOwn(Ympyra.prototype, "pinta"));
console.log(Object.getPrototypeOf(Ympyra.prototype) === Muoto.prototype);
// @loppu luokka
