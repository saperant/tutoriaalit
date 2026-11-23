// Lukee varastotapahtumia riveittäin: tuote;muutos
// Virheelliset rivit raportoidaan, eikä niitä lasketa mukaan.
import { createInterface } from "node:readline";

/** @type {Map<string, number>} */
const saldot = new Map();
let rivinumero = 0;
const rivit = createInterface({ input: process.stdin, crlfDelay: Infinity });

for await (const rivi of rivit) {
  rivinumero += 1;
  if (rivi.trim() === "" || rivi.startsWith("#")) continue;
  const [tuote, teksti, ...ylimaaraiset] = rivi.split(";");
  const muutos = Number(teksti);
  if (!tuote || ylimaaraiset.length > 0 || !Number.isInteger(muutos)) {
    console.log(`rivi ${rivinumero}: virheellinen: ${JSON.stringify(rivi)}`);
    continue;
  }
  saldot.set(tuote.trim(), (saldot.get(tuote.trim()) ?? 0) + muutos);
}

for (const [tuote, saldo] of [...saldot].sort()) {
  console.log(`${tuote.padEnd(10)}${String(saldo).padStart(5)}`);
}
