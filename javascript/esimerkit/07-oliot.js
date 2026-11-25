// @alku literaali
const nimi = "kahvi";
const kentta = "hinta";
const tuote = {
  nimi,                 // lyhennetty: sama kuin nimi: nimi
  [kentta]: 650,        // laskettu avain: kentän nimi on muuttujassa
  tagit: ["juoma", "luomu"],
  kuvaus() {            // metodi
    return `${this.nimi} ${(this.hinta / 100).toFixed(2)} €`;
  },
};
console.log(tuote.kuvaus(), tuote["hinta"], "varasto" in tuote);
// @loppu literaali

// @alku purkaminen
// Olio puretaan kenttien nimillä: uusi nimi kaksoispisteellä, oletusarvo
// yhtäsuuruusmerkillä ja loput kentät loppuoperaattorilla.
const { nimi: tuotenimi, hinta, tagit: [paatagi], ...loput } = tuote;
console.log(tuotenimi, hinta, paatagi, Object.keys(loput));

/** @type {{ portti?: number, isanta?: string }} */
const asetukset = { portti: 8080 };
const { portti = 80, isanta = "localhost" } = asetukset;
console.log(portti, isanta);

// Taulukko puretaan paikan mukaan; pilkku ohittaa alkion.
const [vuosi, , paiva] = "2026-11-23".split("-").map(Number);
let [a, b] = [1, 2];
[a, b] = [b, a];        // vaihto ilman apumuuttujaa
console.log(vuosi, paiva, a, b);
// @loppu purkaminen

// @alku levitys
// Levitys kopioi kentät uuteen olioon; myöhempi kenttä voittaa.
const oletukset = { koko: "M", vari: "musta", lahjapaketti: false };
const valinta = { vari: "sininen" };
console.log({ ...oletukset, ...valinta });
// @loppu levitys

// @alku lapikaynti
/** @type {Record<string, number>} */
const hinnatSentteina = { kahvi: 650, tee: 425, leipä: 310 };
console.log(Object.keys(hinnatSentteina));
for (const [tuote, sentit] of Object.entries(hinnatSentteina)) {
  if (sentit > 400) console.log(tuote, sentit);
}
// entries → muunnos → fromEntries on olion vastine taulukon map-metodille.
const euroina = Object.fromEntries(
  Object.entries(hinnatSentteina).map(([t, s]) => [t, s / 100]),
);
console.log(euroina);
// @loppu lapikaynti
