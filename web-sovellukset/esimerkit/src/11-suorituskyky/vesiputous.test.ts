import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { luoAsiakas } from "../07-verkko/asiakas.ts";
import { TILAT } from "../tilat.ts";
import { haePerakkain, haeRinnakkain } from "./vesiputous.ts";

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); });

/** Vale-fetch, joka vastaa 100 ms:n kuluttua (näennäisaikaa). */
const hidasFetch = (async (osoite: string | URL | Request) => {
  await new Promise((ok) => setTimeout(ok, 100));
  const id = String(osoite).split("/").at(-1);
  return Response.json(TILAT.find((t) => t.id === id));
}) as typeof fetch;

test.each([
  ["peräkkäin", haePerakkain, 300],
  ["rinnakkain", haeRinnakkain, 100],
] as const)("%s kestää %i ms", async (_, hae, kesto) => {
  const alku = Date.now();
  const lupaus = hae(luoAsiakas("", hidasFetch), ["aalto", "kivi", "tove"]);
  await vi.runAllTimersAsync();
  expect((await lupaus).map((t) => t.nimi)).toEqual(["Aalto", "Kivi",
                                                     "Tove"]);
  expect(Date.now() - alku).toBe(kesto);
});
