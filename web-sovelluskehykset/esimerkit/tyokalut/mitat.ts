// Mittaa toteutukset: lähdekoodin rivit ja selaimeen ladattavan
// JavaScriptin koko. Rivit lasketaan lähteistä, koko käännöksestä
// (dist/), joten aja ensin käännös.
//
//   node tyokalut/mitat.ts             tulostaa taulukon
//   node tyokalut/mitat.ts --tarkista  varmistaa kokojen suuruusluokat
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { gzipSync } from "node:zlib";

const JUURI = join(import.meta.dirname, "..");
const LAHTEET: Record<string, string[]> = {
  paljas: ["paljas/main.ts", "paljas/index.html"],
  react: ["react/src"],
  vue: ["vue/src"],
  angular: ["angular/src"],
  svelte: ["svelte/src"],
};

function tiedostot(polku: string): string[] {
  const koko = join(JUURI, polku);
  if (!statSync(koko).isDirectory()) return [koko];
  return readdirSync(koko).flatMap((nimi) => tiedostot(join(polku, nimi)));
}

// @alku mitat
/** Rivit, joilla on koodia: ei tyhjiä rivejä eikä pelkkiä kommentteja. */
function koodirivit(polut: string[]): number {
  const kommentti = /^(\/\/|\/\*|\*|<!--)/;
  return polut.flatMap(tiedostot)
    .flatMap((t) => readFileSync(t, "utf8").split("\n"))
    .map((rivi) => rivi.trim())
    .filter((rivi) => rivi !== "" && !kommentti.test(rivi)).length;
}

/** Käännetyn JavaScriptin koko tavuina: sellaisenaan ja pakattuna. */
function paketti(nimi: string): { raaka: number; gzip: number } {
  const js = tiedostot(`dist/${nimi}`).filter((t) => t.endsWith(".js"))
    .map((t) => readFileSync(t));
  return {
    raaka: js.reduce((summa, t) => summa + t.length, 0),
    gzip: js.reduce((summa, t) => summa + gzipSync(t).length, 0),
  };
}
// @loppu mitat

const kt = (tavut: number) => (tavut / 1000).toFixed(1).padStart(10);
const tulokset = Object.entries(LAHTEET).map(([nimi, polut]) =>
  ({ nimi, rivit: koodirivit(polut), ...paketti(nimi) }));

if (process.argv.includes("--tarkista")) {
  // Tarkat koot riippuvat versioista, suuruusluokat eivät.
  const gzip = Object.fromEntries(tulokset.map((t) => [t.nimi, t.gzip]));
  const jarjestys = ["paljas", "svelte", "vue", "react"];
  const kasvaa = jarjestys.every((nimi, i) =>
    i === 0 || gzip[jarjestys[i - 1]!]! < gzip[nimi]!);
  const kohtuulliset = tulokset.every((t) => t.gzip < 100_000);
  if (!kasvaa || !kohtuulliset || gzip.paljas! > 5_000) {
    console.error("pakettien koot eivät ole odotetussa järjestyksessä");
    process.exit(1);
  }
  console.log("OK: pakettien koot odotetussa suuruusluokassa");
} else {
  console.log("toteutus  koodirivit   JS (kt)  gzip (kt)");
  for (const t of tulokset) {
    console.log(t.nimi.padEnd(9), String(t.rivit).padStart(10),
      kt(t.raaka), kt(t.gzip));
  }
  console.log("yhteinen ",
    String(koodirivit(["yhteinen/logiikka.ts"])).padStart(10),
    "  (kehyksestä riippumaton logiikka)");
}
