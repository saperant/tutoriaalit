import { act, render, renderHook, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { Sekunnit } from "./Laskuri.tsx";
import { useViivastetty } from "./useViivastetty.ts";

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); });

// @alku testi
test("viivastetty arvo päivittyy vasta tauon jälkeen", () => {
  const { result, rerender } = renderHook(
    ({ arvo }) => useViivastetty(arvo, 300), { initialProps: { arvo: "s" } });
  rerender({ arvo: "si" });
  act(() => { vi.advanceTimersByTime(200); });
  rerender({ arvo: "sib" });                 // uusi näppäily nollaa ajan
  act(() => { vi.advanceTimersByTime(200); });
  expect(result.current).toBe("s");
  act(() => { vi.advanceTimersByTime(100); });
  expect(result.current).toBe("sib");
});

test.each([["vanha", "1 s"], ["oikea", "3 s"]] as const)(
  "versio %s näyttää kolmen sekunnin jälkeen %s", (versio, odotettu) => {
    render(<Sekunnit versio={versio} />);
    act(() => { vi.advanceTimersByTime(3000); });
    expect(screen.getByText(odotettu)).toBeDefined();
  });
// @loppu testi
