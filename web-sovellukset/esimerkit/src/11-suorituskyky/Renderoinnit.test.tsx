import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import { Muistiinpanot, type Versio } from "./Renderoinnit.tsx";

// @alku testi
test.each<[Versio, number]>([
  ["tavallinen", 4],          // ensimmäinen + kolme näppäilyä
  ["memo-uusi-funktio", 4],   // uusi funktio-propsi rikkoo vertailun
  ["memo-useCallback", 1],    // propsit samat: lista ohitetaan
])("%s: lista renderöidään %i kertaa", async (versio, kertoja) => {
  let renderointeja = 0;
  const laske = () => { renderointeja += 1; };
  render(<Muistiinpanot versio={versio} laske={laske} />);
  await userEvent.type(screen.getByLabelText("Muistiinpano"), "abc");
  expect(renderointeja).toBe(kertoja);
});
// @loppu testi
