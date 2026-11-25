// Käännösaikainen reaktiivisuus pienoiskoossa (Svelten periaate):
// kääntäjä lukee mallipohjan etukäteen ja tuottaa koodin, joka tietää
// tarkalleen, mitkä tekstisolmut riippuvat mistäkin muuttujasta.
// Selaimeen ei lähetetä vertailijaa eikä mallipohjan tulkkia.

// @alku kaantaja
/** Kääntää mallipohjan, esim. "{nimi}: {maara * hinta} e", moduuliksi. */
function kaanna(pohja: string, muuttujat: string[]): string {
  const osat = pohja.split(/\{([^}]+)\}/);   // parittomat ovat lausekkeita
  const luonti: string[] = [];
  const paivitys = new Map<string, string[]>();
  osat.forEach((osa, i) => {
    if (i % 2 === 0) {
      if (osa !== "") luonti.push(`  teksti(${JSON.stringify(osa)});`);
      return;
    }
    const lauseke = osa.trim().replace(/[a-z]+/g, (sana) =>
      muuttujat.includes(sana) ? `tila.${sana}` : sana);
    luonti.push(`  const t${i} = teksti(${lauseke});`);
    for (const m of muuttujat) {
      if (new RegExp(`\\b${m}\\b`).test(osa)) {
        paivitys.set(m, [...paivitys.get(m) ?? [],
          `t${i}.data = ${lauseke};`]);
      }
    }
  });
  const haarat = [...paivitys].flatMap(([m, rivit]) => [
    `    if (muuttunut === "${m}") {`,
    ...rivit.map((rivi) => `      ${rivi}`), "    }"]);
  return [
    "// tuotettu koodi", ...luonti,
    "  return function paivita(muuttunut) {", ...haarat, "  };",
  ].join("\n");
}
// @loppu kaantaja

// @alku demo
const pohja = "{nimi}: {maara} kpl, yhteensä {maara * hinta} e";
const koodi = kaanna(pohja, ["nimi", "maara", "hinta"]);
console.log(koodi);

// Ajetaan tuotettu koodi. "DOM" on lista tekstisolmuja.
interface Tekstisolmu { data: unknown }
const solmut: Tekstisolmu[] = [];
const teksti = (data: unknown) => {
  const solmu = { data };
  solmut.push(solmu);
  return solmu;
};
const tulosta = () => console.log(solmut.map((s) => s.data).join(""));

const tila = { nimi: "Kahvi", maara: 2, hinta: 4 };
const luo = new Function("tila", "teksti", koodi) as
  (tila: object, teksti: (data: unknown) => Tekstisolmu) =>
    (muuttunut: string) => void;
const paivita = luo(tila, teksti);
tulosta();

// Kääntäjä muuttaa sijoituksen "maara = 3" kahdeksi lauseeksi:
tila.maara = 3;
paivita("maara");
tulosta();
// @loppu demo
