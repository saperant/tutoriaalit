// Kattavuustarkistus: uusi vaihtoehto ilman käsittelyä on käännösvirhe.
type Muoto =
  | { laji: "ympyra"; sade: number }
  | { laji: "suorakulmio"; leveys: number; korkeus: number }
  | { laji: "kolmio"; kanta: number; korkeus: number }; // @virhe: uusi

function eiKasitelty(x: never): never {
  throw new Error(`käsittelemätön tapaus: ${JSON.stringify(x)}`);
}

function ala(m: Muoto): number {
  switch (m.laji) {
    case "ympyra": return Math.PI * m.sade ** 2;
    case "suorakulmio": return m.leveys * m.korkeus;
    default: return eiKasitelty(m); // m on never, jos kaikki käsitelty
  }
}
console.log(ala({ laji: "suorakulmio", leveys: 2, korkeus: 3 }));
