// Rajapinnan reunalla jäsennetään kerran; sisällä luotetaan tyyppeihin.
import { readFileSync } from "node:fs";
import { tilaus, yhteensa, type Tilaus } from "./malli.ts";

function kasittele(t: Tilaus): string {
  const euroa = (yhteensa(t) / 100).toFixed(2);
  return `${t.asiakas}: ${t.rivit.length} riviä, ${euroa} €`;
}

for (const rivi of readFileSync(0, "utf8").split("\n")) {
  if (rivi.trim() === "") continue;
  let data: unknown;
  try {
    data = JSON.parse(rivi);
  } catch {
    console.log("virheellinen JSON");
    continue;
  }
  const t = tilaus(data);
  if (t.ok) console.log(kasittele(t.arvo));
  else for (const v of t.virheet) console.log(`  ${v}`);
}
