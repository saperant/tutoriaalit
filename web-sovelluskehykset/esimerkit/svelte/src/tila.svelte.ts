// Jaettu tila: luokka, jonka kentät ovat reaktiivisia ($state).
// Tiedostopääte .svelte.ts kertoo kääntäjälle, että riimut ($state,
// $derived, $effect) käännetään myös täällä eikä vain komponenteissa.
import * as logiikka from "../../yhteinen/logiikka.ts";
import type { Kiire, Lataus, Tehtava } from "../../yhteinen/logiikka.ts";

// @alku tila
class Tehtavat {
  // $state.raw: reaktiivisuus seuraa sijoitusta kenttään, ei taulukon
  // sisältöä. Logiikka palauttaa aina uuden taulukon.
  lista = $state.raw<readonly Tehtava[]>([]);
  lataus = $state<Lataus>("ladataan");
  // Johdettu arvo: kääntäjä laskee sen uudelleen vain tarvittaessa.
  yhteenveto = $derived(
    this.lataus === "valmis" ? logiikka.yhteenveto(this.lista) : "");

  lataa = () => {
    this.lataus = "ladataan";
    logiikka.haeTehtavat(localStorage).then(
      (haetut) => { this.lista = haetut; this.lataus = "valmis"; },
      () => { this.lataus = "virhe"; },
    );
  };

  lisaa(nimi: string, kiire: Kiire) {
    this.lista = logiikka.lisaa(this.lista, nimi, kiire);
  }
  vaihda(id: number) { this.lista = logiikka.vaihda(this.lista, id); }
  poista(id: number) { this.lista = logiikka.poista(this.lista, id); }
  poistaValmiit = () => {
    this.lista = logiikka.poistaValmiit(this.lista);
  };

  /** Sivuvaikutukset; kutsutaan komponentin $effect-lohkosta. */
  tallenna() {
    if (this.lataus !== "valmis") return;
    logiikka.tallenna(localStorage, this.lista);
    document.title = logiikka.otsikko(this.lista);
  }
}

// Moduulin tasolla luotu olio on koko sovelluksen yhteinen: jokainen
// komponentti, joka tuo sen, lukee samaa tilaa.
export const tehtavat = new Tehtavat();
// @loppu tila
