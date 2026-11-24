import type { Tila } from "../tilat.ts";

// @alku nakyma
export type HakuTila = { haku: string; tilat: readonly Tila[] };

/** Näkymä tilan funktiona: koko näkymä rakennetaan joka kerta alusta. */
export function piirra(juuri: HTMLElement, tila: HakuTila,
                       muuta: (haku: string) => void): void {
  const kentta = document.createElement("input");
  kentta.type = "search";
  kentta.value = tila.haku;
  kentta.setAttribute("aria-label", "Hae tilaa");
  kentta.addEventListener("input", () => muuta(kentta.value));

  const osumat = tila.tilat.filter((t) =>
    t.nimi.toLowerCase().includes(tila.haku.toLowerCase()));
  const lista = document.createElement("ul");
  for (const t of osumat) {
    const kohta = document.createElement("li");
    kohta.textContent = t.nimi;
    lista.append(kohta);
  }
  juuri.replaceChildren(kentta, lista);
}
// @loppu nakyma
