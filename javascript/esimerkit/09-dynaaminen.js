import { basename } from "node:path";

// @alku meta
// import.meta kertoo modulin omat tiedot (CommonJS:n __filename).
console.log(basename(import.meta.filename),
  import.meta.url.startsWith("file:"));
// @loppu meta

// @alku dynaaminen
/**
 * Lataa pakkausmuodon toteutuksen vasta, kun sitä tarvitaan. Modulin
 * lataus on asynkroninen ja tapahtuu kerran; seuraavat kutsut saavat
 * välimuistissa olevan modulin.
 * @param {"gzip" | "brotli"} muoto
 * @param {string} teksti
 */
async function pakkaa(muoto, teksti) {
  const zlib = await import("node:zlib");
  const data = Buffer.from(teksti.repeat(50));
  const pakattu = muoto === "gzip"
    ? zlib.gzipSync(data)
    : zlib.brotliCompressSync(data);
  return pakattu.length < data.length;
}

// Ylimmän tason await: moduli odottaa ennen kuin tuojat jatkavat.
console.log(await pakkaa("gzip", "kahvi;2;650\n"));
// @loppu dynaaminen
