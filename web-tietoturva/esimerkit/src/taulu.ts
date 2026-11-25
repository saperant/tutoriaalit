// Näytösajojen (src/naytos.ts, e2e/*.spec.ts) apufunktiot: tulostaulu
// tasalevyisinä sarakkeina ja hyökkäyksen ajo niin, että virhekin on
// tulos.
import { mkdirSync, writeFileSync } from "node:fs";

export function taulu(otsikot: string[], rivit: string[][]): string {
  const kaikki = [otsikot, ...rivit];
  const leveys = otsikot.map((_, i) =>
    Math.max(...kaikki.map((r) => [...(r[i] ?? "")].length)));
  return kaikki.map((r) => r.map((s, i) =>
    s + " ".repeat(leveys[i]! - [...s].length)).join("  ").trimEnd())
    .join("\n") + "\n";
}

export async function yrita(f: () => unknown): Promise<string> {
  try {
    return String(await f());
  } catch (virhe) {
    return `virhe: ${(virhe as Error).message}`;
  }
}

// Selaintestit kirjoittavat taulunsa tiedostoon, jota make vertaa
// tallennettuun (naytos/*.odotettu).
export function tallenna(nimi: string, sisalto: string): void {
  mkdirSync("test-results/naytos", { recursive: true });
  writeFileSync(`test-results/naytos/${nimi}.txt`, sisalto);
}
