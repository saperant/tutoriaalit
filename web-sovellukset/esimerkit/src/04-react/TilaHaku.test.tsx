import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";
import { TILAT } from "../tilat.ts";
import { TilaHaku } from "./TilaHaku.tsx";

// @alku testi
test("haku suodattaa listan ja fokus säilyy", async () => {
  const kayttaja = userEvent.setup();
  const onVaraa = vi.fn();
  render(<TilaHaku tilat={TILAT} onVaraa={onVaraa} />);

  const kentta = screen.getByRole("searchbox", { name: "Hae nimellä" });
  await kayttaja.type(kentta, "si");
  expect(screen.getByText("1 / 4 tilaa")).toBeDefined();
  expect(document.activeElement).toBe(kentta);   // vrt. luku 3

  const nappi = screen.getByRole("button", { name: "Varaa Sibelius" });
  await kayttaja.click(nappi);
  expect(onVaraa).toHaveBeenCalledWith("sibelius");
});

test("tyhjä tulos kerrotaan", async () => {
  const kayttaja = userEvent.setup();
  render(<TilaHaku tilat={TILAT} onVaraa={() => {}} />);
  const paikat = screen.getByRole("spinbutton");
  await kayttaja.clear(paikat);
  await kayttaja.type(paikat, "50");
  expect(screen.getByText("Ei hakuehtoja vastaavia tiloja.")).toBeDefined();
});
// @loppu testi
