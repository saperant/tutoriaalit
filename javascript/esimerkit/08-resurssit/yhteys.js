/** Tietokantayhteyden malli: kirjaa avaamisen ja sulkemisen. */
export class Yhteys {
  #nimi;
  #auki = true;

  /** @param {string} nimi */
  constructor(nimi) {
    this.#nimi = nimi;
    console.log(`avattu ${nimi}`);
  }

  /** @param {string} kysely */
  kysy(kysely) {
    if (!this.#auki) throw new Error("yhteys on suljettu");
    if (kysely.includes("DROP")) throw new Error("kysely hylättiin");
    return `${this.#nimi}: ${kysely}`;
  }

  // Vapautusprotokolla: using-määrittely kutsuu tätä metodia, kun
  // lohko päättyy. Metodin pitää sietää toistuva kutsu.
  [Symbol.dispose]() {
    if (!this.#auki) return;
    this.#auki = false;
    console.log(`suljettu ${this.#nimi}`);
  }
}
