import { expect, test } from "vitest";
import { TILAT } from "../tilat.ts";
import { type HakuTila, piirra } from "./nakyma.ts";

// @alku testi
test("uudelleenrakennus hävittää fokuksen", () => {
  const juuri = document.createElement("div");
  document.body.replaceChildren(juuri);
  let tila: HakuTila = { haku: "", tilat: TILAT };
  const muuta = (haku: string) => {
    tila = { ...tila, haku };            // uusi tila, ei mutaatiota
    piirra(juuri, tila, muuta);
  };
  piirra(juuri, tila, muuta);

  const kentta = juuri.querySelector("input")!;
  kentta.focus();
  kentta.value = "ki";
  kentta.dispatchEvent(new Event("input"));

  expect(juuri.querySelectorAll("li")).toHaveLength(1);    // näkymä oikein
  expect(document.activeElement).not.toBe(juuri.querySelector("input"));
});
// @loppu testi
