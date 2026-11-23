class Laskuri {
  arvo = 0;

  kasvata() {
    this.arvo += 1;
  }
}

const laskuri = new Laskuri();
laskuri.kasvata(); // this = laskuri
console.log(laskuri.arvo);

// Metodi irrotetaan oliosta: this on nyt undefined.
const irrotettu = laskuri.kasvata;
[1, 2].forEach(irrotettu);
