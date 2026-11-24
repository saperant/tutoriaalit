import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test } from "vitest";
import {
  Linkki, sovita, useHakuparametri, useSijainti,
} from "./reititin.tsx";

beforeEach(() => history.replaceState(null, "", "/"));

function Polku() {
  return <p>polku {useSijainti().pathname}</p>;
}

// @alku testi
test("sovita poimii parametrit", () => {
  expect(sovita("/tilat/:id", "/tilat/sibelius")).toEqual({ id: "sibelius" });
  expect(sovita("/tilat/:id", "/tilat")).toBeNull();
  expect(sovita("/tilat/:id", "/varaukset/v1")).toBeNull();
});

test("linkki siirtyy ilman latausta, ctrl-klikkaus ei", async () => {
  render(<><Linkki to="/tilat/kivi">Kivi</Linkki><Polku /></>);
  const linkki = screen.getByRole("link", { name: "Kivi" });

  fireEvent.click(linkki, { ctrlKey: true });     // selaimen oma käytös
  expect(screen.getByText("polku /")).toBeDefined();

  await userEvent.click(linkki);
  expect(screen.getByText("polku /tilat/kivi")).toBeDefined();
  expect(history.length).toBeGreaterThan(1);
});

test("hakuparametri päivittää osoitteen", async () => {
  function Haku() {
    const [haku, setHaku] = useHakuparametri("haku");
    return <input aria-label="Haku" value={haku}
                  onChange={(e) => setHaku(e.target.value)} />;
  }
  render(<Haku />);
  await userEvent.type(screen.getByLabelText("Haku"), "si");
  expect(location.search).toBe("?haku=si");
});
// @loppu testi
