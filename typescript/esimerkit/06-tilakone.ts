// Tilauksen elinkaari eroteltuna unionina: jokaisessa tilassa on vain
// siihen kuuluvat tiedot, joten mahdottomia tiloja ei voi esittää.
type Tilaus =
  | { tila: "luonnos"; rivit: string[] }
  | { tila: "maksettu"; rivit: string[]; maksuviite: string }
  | { tila: "lahetetty"; rivit: string[]; seurantakoodi: string }
  | { tila: "peruttu"; syy: string };

type Tapahtuma =
  | { tyyppi: "maksu"; viite: string }
  | { tyyppi: "lahetys"; koodi: string }
  | { tyyppi: "peruutus"; syy: string };

function siirry(t: Tilaus, e: Tapahtuma): Tilaus {
  switch (t.tila) {
    case "luonnos":
      if (e.tyyppi === "maksu") {
        return { tila: "maksettu", rivit: t.rivit, maksuviite: e.viite };
      }
      if (e.tyyppi === "peruutus") return { tila: "peruttu", syy: e.syy };
      break;
    case "maksettu":
      if (e.tyyppi === "lahetys") {
        return { tila: "lahetetty", rivit: t.rivit, seurantakoodi: e.koodi };
      }
      break;
    case "lahetetty":
    case "peruttu":
      break; // lopputiloja
  }
  throw new Error(`tapahtuma ${e.tyyppi} ei sovi tilaan ${t.tila}`);
}

function kuvaa(t: Tilaus): string {
  switch (t.tila) {
    case "luonnos": return `luonnos, ${t.rivit.length} riviä`;
    case "maksettu": return `maksettu (viite ${t.maksuviite})`;
    case "lahetetty": return `lähetetty, seuranta ${t.seurantakoodi}`;
    case "peruttu": return `peruttu: ${t.syy}`;
  }
} // ei puuttuvaa paluuarvoa: switch kattaa kaikki tilat

let t: Tilaus = { tila: "luonnos", rivit: ["omena", "leipä"] };
const tapahtumat: Tapahtuma[] = [
  { tyyppi: "maksu", viite: "RF18 1234" },
  { tyyppi: "lahetys", koodi: "JJFI6400" },
  { tyyppi: "peruutus", syy: "asiakas perui" },
];
for (const e of tapahtumat) {
  try {
    t = siirry(t, e);
    console.log(kuvaa(t));
  } catch (virhe) {
    console.log(virhe instanceof Error ? virhe.message : virhe);
  }
}
