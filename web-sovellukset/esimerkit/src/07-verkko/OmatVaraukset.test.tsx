import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import { OmatVaraukset, type Varaus } from "./OmatVaraukset.tsx";

const VARAUKSET: Varaus[] = [
  { id: "v1", tila: "Aalto", aika: "1.12. 9.00" },
  { id: "v2", tila: "Kivi", aika: "2.12. 13.00" },
];

// @alku testi
test("hylätty peruutus palauttaa varauksen", async () => {
  const kayttaja = userEvent.setup();
  let hylkaa!: (syy: Error) => void;
  const peru = () => new Promise<void>((_, h) => { hylkaa = h; });
  render(<OmatVaraukset alku={VARAUKSET} peru={peru} />);

  await kayttaja.click(screen.getByRole("button",
                                        { name: "Peru Aalto 1.12. 9.00" }));
  expect(screen.queryByText(/^Aalto/)).toBeNull();     // poistui heti
  hylkaa(new Error("500"));
  expect(await screen.findByText(/^Aalto/)).toBeDefined();
  expect(screen.getByRole("alert").textContent)
    .toBe("Varauksen Aalto 1.12. 9.00 peruutus epäonnistui.");
  expect(screen.getAllByRole("listitem")[0]?.textContent)
    .toMatch(/^Aalto/);                                  // järjestys säilyy
});
// @loppu testi
