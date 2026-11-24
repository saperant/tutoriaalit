import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { KayttajaTarjoaja, Tervehdys } from "./Kayttaja.tsx";

test("konteksti välittää käyttäjän syvälle puuhun", () => {
  render(
    <KayttajaTarjoaja kayttaja={{ nimi: "Aino", rooli: "yllapitaja" }}>
      <main><Tervehdys /></main>
    </KayttajaTarjoaja>);
  expect(screen.getByText("Kirjautunut: Aino (ylläpito)")).toBeDefined();
});

test("ilman tarjoajaa virhe on selvä", () => {
  vi.spyOn(console, "error").mockImplementation(() => {});
  expect(() => render(<Tervehdys />))
    .toThrow("useKayttaja vaatii KayttajaTarjoajan");
});
