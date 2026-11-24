import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";
import { VarausLomake } from "./VarausLomake.tsx";

// @alku testi
test("virheet näytetään ja fokus siirtyy ensimmäiseen", async () => {
  const kayttaja = userEvent.setup();
  const laheta = vi.fn<(l: unknown) => Promise<string>>();
  render(<VarausLomake tilaId="kivi" tanaan="2026-11-24" laheta={laheta} />);

  await kayttaja.click(screen.getByRole("button", { name: "Varaa" }));
  // Kenttä löytyy nimellä ja kuvauksella, kuten ruudunlukija sen esittää.
  const aihe = screen.getByRole("textbox", {
    name: "Aihe", description: "Kirjoita aihe (väh. 3 merkkiä).",
  });
  expect(aihe.getAttribute("aria-invalid")).toBe("true");
  expect(document.activeElement).toBe(aihe);
  expect(laheta).not.toHaveBeenCalled();
});

test("epäonnistunut lähetys säilyttää arvot", async () => {
  const kayttaja = userEvent.setup();
  const laheta = vi.fn()
    .mockRejectedValueOnce(new Error("Tila on jo varattu."))
    .mockResolvedValueOnce("v42");
  render(<VarausLomake tilaId="kivi" tanaan="2026-11-24" laheta={laheta} />);

  await kayttaja.type(screen.getByLabelText("Aihe"), "Retro");
  await kayttaja.click(screen.getByRole("button", { name: "Varaa" }));
  expect((await screen.findByRole("alert")).textContent)
    .toBe("Tila on jo varattu.");
  expect(screen.getByLabelText<HTMLInputElement>("Aihe").value).toBe("Retro");

  await kayttaja.click(screen.getByRole("button", { name: "Varaa" }));
  expect((await screen.findByRole("status")).textContent)
    .toBe("Varaus tehty (tunnus v42).");
  expect(laheta).toHaveBeenLastCalledWith(
    expect.objectContaining({ tilaId: "kivi", aihe: "Retro" }));
});
// @loppu testi
