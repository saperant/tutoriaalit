class Laskuri {
  #arvo = 0;

  kasvata() {
    return ++this.#arvo;
  }
}

const laskuri = new Laskuri();
laskuri.kasvata();
console.log(laskuri.kasvata());
laskuri.#arvo = 100; // @virhe
