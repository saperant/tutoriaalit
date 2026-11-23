// Rakenteellinen tyypitys: tyyppi on yhteensopiva, jos rakenne täsmää.
type Euro = { maara: number };
type Paino = { maara: number }; // kilogrammoina

function hinnoittele(hinta: Euro): string {
  return `${hinta.maara.toFixed(2)} €`;
}

const paino: Paino = { maara: 1.5 };
console.log(hinnoittele(paino)); // kelpaa: rakenne on sama

// Ylimääräiset kentät eivät haittaa, kun arvo ei ole tuore literaali.
const tuote = { maara: 2.9, nimi: "leipä" };
console.log(hinnoittele(tuote));
