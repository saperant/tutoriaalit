// Lukee tilausrivit muodossa "tuote;määrä;yksikköhinta" ja tulostaa
// tuotekohtaiset summat. Virheelliset rivit raportoidaan.
import { readFileSync } from "node:fs";

type Tilausrivi = {
  readonly tuote: string;
  readonly maara: number;
  readonly hinta: number; // euroina
};

type Jasennys =
  | { ok: true; rivi: Tilausrivi }
  | { ok: false; virhe: string };

function jasenna(teksti: string): Jasennys {
  const kentat = teksti.split(";");
  if (kentat.length !== 3) {
    return { ok: false, virhe: "odotettiin kolme kenttää" };
  }
  const [tuote, maara, hinta] = kentat.map((k) => k.trim());
  const m = Number(maara);
  const h = Number(hinta?.replace(",", "."));
  if (!tuote) return { ok: false, virhe: "tuote puuttuu" };
  if (!Number.isInteger(m) || m <= 0) {
    return { ok: false, virhe: `virheellinen määrä '${maara}'` };
  }
  if (!Number.isFinite(h) || h < 0) {
    return { ok: false, virhe: `virheellinen hinta '${hinta}'` };
  }
  return { ok: true, rivi: { tuote, maara: m, hinta: h } };
}

const summat = new Map<string, number>();
const rivit = readFileSync(0, "utf8").split("\n");
rivit.forEach((teksti, i) => {
  if (teksti.trim() === "") return;
  const tulos = jasenna(teksti);
  if (!tulos.ok) {
    console.log(`rivi ${i + 1}: ${tulos.virhe}`);
    return;
  }
  const { tuote, maara, hinta } = tulos.rivi;
  summat.set(tuote, (summat.get(tuote) ?? 0) + maara * hinta);
});

for (const [tuote, summa] of summat) {
  console.log(`${tuote.padEnd(10)} ${summa.toFixed(2).padStart(8)}`);
}
