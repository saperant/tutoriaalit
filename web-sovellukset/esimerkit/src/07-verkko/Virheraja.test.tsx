import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";
import { Virheraja } from "./Virheraja.tsx";

// @alku testi
let rikki = true;
function Varusteet() {
  if (rikki) throw new Error("varusteet puuttuvat");
  return <p>Varusteet: näyttö</p>;
}

test("virheraja näyttää varanäkymän ja toipuu", async () => {
  const kayttaja = userEvent.setup();
  const ilmoita = vi.fn();
  vi.spyOn(console, "error").mockImplementation(() => {});  // Reactin loki
  render(
    <main>
      <h1>Kivi</h1>
      <Virheraja ilmoita={ilmoita}><Varusteet /></Virheraja>
    </main>);

  // Vain rajan sisäpuoli korvautuu; otsikko on yhä paikallaan.
  expect(screen.getByRole("heading", { name: "Kivi" })).toBeDefined();
  expect(screen.getByRole("alert").textContent)
    .toContain("Näkymää ei voitu näyttää.");
  expect(ilmoita.mock.calls[0]?.[0]).toEqual(
    new Error("varusteet puuttuvat"));

  rikki = false;                       // vika korjaantuu
  await kayttaja.click(screen.getByRole("button",
                                        { name: "Yritä uudelleen" }));
  expect(screen.getByText("Varusteet: näyttö")).toBeDefined();
  expect(screen.queryByRole("alert")).toBeNull();
});
// @loppu testi
