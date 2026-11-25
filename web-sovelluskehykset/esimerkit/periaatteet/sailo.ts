// Tilasäilö pienoiskoossa (Reduxin, Pinian ja NgRx:n yhteinen ydin):
// yksi tila, jota muutetaan vain nimetyillä toiminnoilla, ja tilaajat,
// joille muutoksesta ilmoitetaan. Säilö ei tiedä kehyksistä mitään.
import * as logiikka from "../yhteinen/logiikka.ts";
import type { Kiire, Tehtava } from "../yhteinen/logiikka.ts";

// @alku sailo
type Tilaaja = () => void;

function luoSailo<Tila, Toiminto>(
  alku: Tila, muunna: (tila: Tila, toiminto: Toiminto) => Tila,
) {
  let tila = alku;
  const tilaajat = new Set<Tilaaja>();
  return {
    lue: () => tila,
    laheta(toiminto: Toiminto): void {
      tila = muunna(tila, toiminto);      // ainoa paikka, jossa tila muuttuu
      for (const tilaaja of tilaajat) tilaaja();
    },
    /** Palauttaa funktion, jolla tilaus perutaan. */
    tilaa(tilaaja: Tilaaja): () => void {
      tilaajat.add(tilaaja);
      return () => { tilaajat.delete(tilaaja); };
    },
  };
}
// @loppu sailo

// @alku demo
type Toiminto =
  | { tyyppi: "lisaa"; nimi: string; kiire: Kiire }
  | { tyyppi: "vaihda"; id: number };

function muunna(tila: readonly Tehtava[], t: Toiminto): Tehtava[] {
  switch (t.tyyppi) {
    case "lisaa": return logiikka.lisaa(tila, t.nimi, t.kiire);
    case "vaihda": return logiikka.vaihda(tila, t.id);
  }
}

const sailo = luoSailo<readonly Tehtava[], Toiminto>([], muunna);
// Loki on toimintojen historia: jokainen muutos on nimetty ja toistettava.
const loki: Toiminto[] = [];
const laheta = (t: Toiminto) => { loki.push(t); sailo.laheta(t); };

const peru = sailo.tilaa(() =>
  console.log(`  [yhteenveto] ${logiikka.yhteenveto(sailo.lue())}`));

console.log("Lähetetään kolme toimintoa:");
laheta({ tyyppi: "lisaa", nimi: "Varaa kokoushuone", kiire: "tavallinen" });
laheta({ tyyppi: "lisaa", nimi: "Tilaa kahvit", kiire: "kiireellinen" });
laheta({ tyyppi: "vaihda", id: 1 });
peru();

// Sama historia tuottaa tyhjästä aloittaen saman tilan.
const toistettu = loki.reduce(muunna, [] as readonly Tehtava[]);
console.log("Toistettu historiasta:",
  JSON.stringify(toistettu) === JSON.stringify(sailo.lue()));
// @loppu demo
