// Muutostentunnistus pienoiskoossa (AngularJS:n ja Angularin
// alkuperäinen periaate): tila on tavallisia olioita, joita muutetaan
// suoraan. Kehys ei tiedä, mikä muuttui, joten jokaisen tapahtuman
// jälkeen se laskee kaikki mallipohjan sidokset ja vertaa edelliseen.

// @alku ydin
interface Sidos { kohta: string; lue: () => string; edellinen?: string }

class Nakyma {
  private readonly sidokset: Sidos[] = [];

  /** Mallipohjan {{ lauseke }}: DOM:n kohta ja sen arvon laskeva funktio. */
  sido(kohta: string, lue: () => string): void {
    this.sidokset.push({ kohta, lue });
  }

  /** Lukee jokaisen sidoksen ja päivittää ne, joiden arvo muuttui. */
  tarkista(): void {
    const paivitetyt: string[] = [];
    for (const sidos of this.sidokset) {
      const arvo = sidos.lue();
      if (arvo !== sidos.edellinen) {
        sidos.edellinen = arvo;
        paivitetyt.push(`${sidos.kohta} = "${arvo}"`);
      }
    }
    console.log(`  tarkistettu ${this.sidokset.length} sidosta, ` +
      `päivitetty ${paivitetyt.length}`);
    for (const p of paivitetyt) console.log(`    ${p}`);
  }

  /** Kehys kietoo tapahtumankäsittelijät: ensin käsittelijä, sitten
   *  tarkistus. Angularissa tämän teki pitkään zone.js-kirjasto. */
  tapahtuma(nimi: string, kasittelija: () => void): void {
    console.log(`${nimi}:`);
    kasittelija();
    this.tarkista();
  }
}
// @loppu ydin

// @alku demo
const tila = {
  tehtavat: [
    { nimi: "Varaa kokoushuone", valmis: false },
    { nimi: "Lähetä esityslista", valmis: true },
  ],
  vainAvoimet: false,
};

const nakyma = new Nakyma();
nakyma.sido("yhteenveto", () =>
  `avoimia ${tila.tehtavat.filter((t) => !t.valmis).length}`);
nakyma.sido("lista", () => tila.tehtavat
  .filter((t) => !tila.vainAvoimet || !t.valmis)
  .map((t) => t.nimi).join(", "));
nakyma.sido("suodatin", () => tila.vainAvoimet ? "avoimet" : "kaikki");

console.log("Ensimmäinen piirto:");
nakyma.tarkista();
// Käsittelijät muuttavat tilaa suoraan, ilman set-kutsuja tai kopioita.
nakyma.tapahtuma("Suodatin päälle", () => { tila.vainAvoimet = true; });
nakyma.tapahtuma("Merkitään ensimmäinen valmiiksi", () => {
  const eka = tila.tehtavat[0];
  if (eka !== undefined) eka.valmis = true;
});
nakyma.tapahtuma("Hiiri liikkuu (tila ei muutu)", () => {});
// @loppu demo
