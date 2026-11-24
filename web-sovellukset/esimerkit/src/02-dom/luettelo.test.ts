import { beforeEach, expect, test } from "vitest";
import { TILAT } from "../tilat.ts";
import { kuunteleVarauksia, piirraTilat } from "./luettelo.ts";

let juuri: HTMLElement;
beforeEach(() => {
  document.body.innerHTML = `<div id="tilat"></div>`;
  juuri = document.getElementById("tilat")!;
});

// @alku testi
test("delegoitu kuuntelija tunnistaa napin", () => {
  const valitut: string[] = [];
  const lopeta = kuunteleVarauksia(juuri, (id) => valitut.push(id));
  piirraTilat(juuri, TILAT);              // napit luodaan kuuntelun jälkeen
  juuri.querySelector<HTMLButtonElement>("[data-tila=kivi]")!.click();
  lopeta();
  juuri.querySelector<HTMLButtonElement>("[data-tila=tove]")!.click();
  expect(valitut).toEqual(["kivi"]);
});

test("nimi on tekstiä, ei HTML:ää", () => {
  const nimi = "<img src=x onerror=alert(1)>";
  piirraTilat(juuri, [{ ...TILAT[0]!, nimi }]);
  expect(juuri.querySelector("img")).toBeNull();
  expect(juuri.textContent).toContain("<img src=x");
});
// @loppu testi
