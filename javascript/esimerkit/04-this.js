// @alku saannot
class Ajastin {
  nimi = "ajastin";

  tavallinen() {
    return this?.nimi;
  }

  // Luokan kenttään tallennettu nuolifunktio sitoo this-arvon olioon.
  nuoli = () => this.nimi;
}

const ajastin = new Ajastin();
const { tavallinen, nuoli } = ajastin;
console.log(ajastin.tavallinen(), tavallinen(), nuoli());
console.log(tavallinen.call({ nimi: "vieras" }));
console.log(ajastin.tavallinen.bind(ajastin)());
// @loppu saannot

// @alku takaisinkutsu
class Mittari {
  /** @type {number[]} */
  lukemat = [];

  /** @param {number[]} uudet */
  lisaa(uudet) {
    // Nuolifunktio perii this-arvon ympäröivästä metodista.
    uudet.forEach((arvo) => this.lukemat.push(arvo));
    return this;
  }
}
console.log(new Mittari().lisaa([3, 4]).lisaa([5]).lukemat);
// @loppu takaisinkutsu
