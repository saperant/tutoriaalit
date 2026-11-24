import type { Tila } from "../tilat.ts";

// @alku piirra
/** Piirtää tilaluettelon. Teksti asetetaan textContent-ominaisuuteen,
 *  joten nimessä oleva HTML näkyy tekstinä eikä suoritu. */
export function piirraTilat(juuri: HTMLElement, tilat: readonly Tila[]) {
  const lista = document.createElement("ul");
  for (const tila of tilat) {
    const kohta = document.createElement("li");
    const nimi = document.createElement("span");
    nimi.textContent = `${tila.nimi} (${tila.paikkoja} hlöä)`;
    const nappi = document.createElement("button");
    nappi.type = "button";
    nappi.textContent = "Varaa";
    nappi.dataset.tila = tila.id;     // data-tila="aalto"
    kohta.append(nimi, " ", nappi);
    lista.append(kohta);
  }
  juuri.replaceChildren(lista);
}
// @loppu piirra

// @alku delegointi
/** Yksi kuuntelija koko luettelolle (tapahtumien delegointi). Toimii
 *  myös napeille, jotka luodaan vasta myöhemmin. */
export function kuunteleVarauksia(
  juuri: HTMLElement,
  kasittelija: (tilaId: string) => void,
): () => void {
  const kuuntelija = (e: Event) => {
    if (!(e.target instanceof Element)) return;
    const nappi = e.target.closest<HTMLButtonElement>("button[data-tila]");
    if (nappi && juuri.contains(nappi) && nappi.dataset.tila) {
      kasittelija(nappi.dataset.tila);
    }
  };
  juuri.addEventListener("click", kuuntelija);
  return () => juuri.removeEventListener("click", kuuntelija);
}
// @loppu delegointi
