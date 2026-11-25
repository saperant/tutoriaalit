// Laskee lukitustiedostosta, montako pakettia kukin kehys tuo mukanaan:
// ajonaikaiset (selaimeen päätyvät) ja kehitystyökalut erikseen.
// Valinnaisia, alustakohtaisia paketteja ei lasketa.
import { readFileSync } from "node:fs";
import { join } from "node:path";

interface Paketti {
  version?: string;
  optional?: boolean;
  dependencies?: Record<string, string>;
  peerDependencies?: Record<string, string>;
}

const lukitus = JSON.parse(readFileSync(
  join(import.meta.dirname, "..", "package-lock.json"), "utf8")) as
  { packages: Record<string, Paketti> };

// @alku sulkeuma
/** Etsii riippuvuuden kuten Node: lähimmästä node_modules-hakemistosta. */
function etsi(mista: string, nimi: string): string | null {
  for (let polku = mista; ; polku = polku.replace(
    /\/?node_modules\/(@[^/]+\/)?[^/]+$/, "")) {
    const ehdokas = `${polku}${polku ? "/" : ""}node_modules/${nimi}`;
    if (lukitus.packages[ehdokas] !== undefined) return ehdokas;
    if (polku === "") return null;
  }
}

/** Kaikki paketit, jotka annetut paketit tarvitsevat suoraan tai
 *  välillisesti. */
function sulkeuma(juuret: string[]): Set<string> {
  const loydetyt = new Set<string>();
  const jono = juuret.map((nimi) => `node_modules/${nimi}`);
  for (let polku = jono.pop(); polku !== undefined; polku = jono.pop()) {
    const paketti = lukitus.packages[polku];
    if (paketti === undefined || paketti.optional === true) continue;
    if (loydetyt.has(polku)) continue;
    loydetyt.add(polku);
    const tarpeet = { ...paketti.peerDependencies, ...paketti.dependencies };
    for (const nimi of Object.keys(tarpeet)) {
      const kohde = etsi(polku, nimi);
      if (kohde !== null) jono.push(kohde);
    }
  }
  return loydetyt;
}
// @loppu sulkeuma

const KEHYKSET: Record<string, { ajo: string[]; tyokalut: string[] }> = {
  react: { ajo: ["react", "react-dom"], tyokalut: ["vite", "typescript"] },
  vue: {
    ajo: ["vue"],
    tyokalut: ["vite", "typescript", "@vitejs/plugin-vue", "vue-tsc"],
  },
  angular: {
    ajo: ["@angular/core", "@angular/common", "@angular/forms",
          "@angular/platform-browser", "rxjs"],
    tyokalut: ["typescript", "@angular/cli", "@angular/build",
               "@angular/compiler-cli"],
  },
  svelte: {
    ajo: ["svelte"],
    tyokalut: ["vite", "typescript", "@sveltejs/vite-plugin-svelte",
               "svelte-check"],
  },
};

console.log("kehys     ajonaikaiset  kehitystyökalut");
for (const [nimi, { ajo, tyokalut }] of Object.entries(KEHYKSET)) {
  const ajossa = sulkeuma(ajo);
  const kaikki = sulkeuma([...ajo, ...tyokalut]);
  console.log(nimi.padEnd(9), String(ajossa.size).padStart(12),
    String(kaikki.size - ajossa.size).padStart(16));
}
