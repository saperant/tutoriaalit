import { act, renderHook } from "@testing-library/react";
import { expect, test } from "vitest";
import { useHaku } from "./useHaku.ts";

/** Lupaus, jonka testi ratkaisee itse haluamassaan järjestyksessä. */
function viivastetty<T>() {
  let ratkaise!: (arvo: T) => void;
  const lupaus = new Promise<T>((r) => { ratkaise = r; });
  return { lupaus, ratkaise };
}

// @alku testi
test("hidas vanha vastaus ei korvaa uutta", async () => {
  const vastaukset = { aalto: viivastetty<string>(),
                       kivi: viivastetty<string>() };
  const peruttu: string[] = [];
  const { result, rerender } = renderHook(({ id }) =>
    useHaku(id, (signal) => {
      signal.addEventListener("abort", () => peruttu.push(id));
      return vastaukset[id].lupaus;
    }), { initialProps: { id: "aalto" as "aalto" | "kivi" } });

  rerender({ id: "kivi" });               // käyttäjä vaihtaa tilaa
  await act(async () => vastaukset.kivi.ratkaise("Kivi"));
  await act(async () => vastaukset.aalto.ratkaise("Aalto"));  // myöhässä

  expect(result.current).toMatchObject({ tila: "valmis", data: "Kivi" });
  expect(peruttu).toEqual(["aalto"]);
});
// @loppu testi

test("virhe ja uusi yritys", async () => {
  let kerta = 0;
  const { result } = renderHook(() => useHaku("aalto", async () => {
    kerta += 1;
    if (kerta === 1) throw new Error("Verkkovirhe");
    return "Aalto";
  }));
  await act(async () => {});
  expect(result.current).toMatchObject({ tila: "virhe" });
  await act(async () => result.current.yritaUudelleen());
  expect(result.current).toMatchObject({ tila: "valmis", data: "Aalto" });
});
