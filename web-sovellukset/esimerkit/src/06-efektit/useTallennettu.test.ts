import { act, renderHook } from "@testing-library/react";
import { beforeEach, expect, test } from "vitest";
import { useTallennettu } from "./useTallennettu.ts";

const jasennaKoko = (x: unknown) =>
  x === "pieni" || x === "suuri" ? x : null;

beforeEach(() => localStorage.clear());

test("arvo tallentuu ja jaetaan saman avaimen käyttäjille", () => {
  const a = renderHook(() => useTallennettu("koko", "pieni", jasennaKoko));
  const b = renderHook(() => useTallennettu("koko", "pieni", jasennaKoko));
  act(() => a.result.current[1]("suuri"));
  expect(b.result.current[0]).toBe("suuri");
  expect(localStorage.getItem("koko")).toBe('"suuri"');
});

test("kelvoton tallennettu arvo korvataan oletuksella", () => {
  localStorage.setItem("koko", "{rikki");
  const { result } = renderHook(
    () => useTallennettu("koko", "pieni", jasennaKoko));
  expect(result.current[0]).toBe("pieni");
});
