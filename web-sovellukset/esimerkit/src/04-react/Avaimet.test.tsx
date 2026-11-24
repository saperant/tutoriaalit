import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import { Osallistujat } from "./Avaimet.tsx";

const RIVIT = [{ id: 1, nimi: "Aino" }, { id: 2, nimi: "Eino" }];

// @alku testi
async function poistaAino(avain: "id" | "indeksi") {
  const kayttaja = userEvent.setup();
  const { unmount } = render(<Osallistujat alku={RIVIT} avain={avain} />);
  await kayttaja.type(screen.getByLabelText("Aino"), "kasvisruoka");
  await kayttaja.click(screen.getByRole("button", { name: "Poista Aino" }));
  const arvo = (screen.getByLabelText("Eino") as HTMLInputElement).value;
  unmount();
  return arvo;
}

test("indeksiavaimella Ainon tila siirtyy Einolle", async () => {
  expect(await poistaAino("indeksi")).toBe("kasvisruoka");
});

test("vakaalla avaimella tila pysyy oikealla rivillä", async () => {
  expect(await poistaAino("id")).toBe("");
});
// @loppu testi
