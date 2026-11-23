// Parametriominaisuus (parameter property) ei ole poistettavaa syntaksia.
class Tuote {
  constructor(readonly nimi: string, readonly hinta: number) {} // @virhe
}

// Poistettava vastine: kentät ja sijoitukset erikseen.
class Tuote2 {
  readonly nimi: string;
  readonly hinta: number;
  constructor(nimi: string, hinta: number) {
    this.nimi = nimi;
    this.hinta = hinta;
  }
}
console.log(new Tuote2("omena", 0.45));
