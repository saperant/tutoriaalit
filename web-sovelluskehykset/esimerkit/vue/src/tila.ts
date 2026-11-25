// Jaettu tila: reaktiiviset viittaukset (ref) ja niitä muuttavat
// funktiot. Komponentit saavat tilan provide/inject-parilla.
import {
  inject, ref, shallowRef, watchEffect, type InjectionKey,
} from "vue";
import * as logiikka from "../../yhteinen/logiikka.ts";
import type { Kiire, Lataus, Tehtava } from "../../yhteinen/logiikka.ts";

// @alku tila
export function luoTehtavat() {
  // shallowRef: reaktiivisuus seuraa sijoitusta .value-kenttään, ei
  // taulukon sisältöä. Logiikka palauttaa aina uuden taulukon.
  const tehtavat = shallowRef<readonly Tehtava[]>([]);
  const lataus = ref<Lataus>("ladataan");

  function lataa() {
    lataus.value = "ladataan";
    logiikka.haeTehtavat(localStorage).then(
      (haetut) => { tehtavat.value = haetut; lataus.value = "valmis"; },
      () => { lataus.value = "virhe"; },
    );
  }
  lataa();

  // Efekti ajetaan uudelleen aina, kun jokin sen lukema arvo muuttuu.
  // Riippuvuuksia ei luetella: Vue kirjaa ne ajon aikana.
  watchEffect(() => {
    if (lataus.value !== "valmis") return;
    logiikka.tallenna(localStorage, tehtavat.value);
    document.title = logiikka.otsikko(tehtavat.value);
  });

  return {
    tehtavat, lataus, lataa,
    lisaa(nimi: string, kiire: Kiire) {
      tehtavat.value = logiikka.lisaa(tehtavat.value, nimi, kiire);
    },
    vaihda(id: number) {
      tehtavat.value = logiikka.vaihda(tehtavat.value, id);
    },
    poista(id: number) {
      tehtavat.value = logiikka.poista(tehtavat.value, id);
    },
    poistaValmiit() {
      tehtavat.value = logiikka.poistaValmiit(tehtavat.value);
    },
  };
}
// @loppu tila

// @alku inject
type Tehtavat = ReturnType<typeof luoTehtavat>;
export const TEHTAVAT: InjectionKey<Tehtavat> = Symbol("tehtavat");

export function useTehtavat(): Tehtavat {
  const tila = inject(TEHTAVAT);
  if (tila === undefined) throw new Error("tehtäviä ei ole tarjottu");
  return tila;
}
// @loppu inject
