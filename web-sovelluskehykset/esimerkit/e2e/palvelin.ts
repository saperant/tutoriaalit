// Playwrightin globalSetup: palvelee käännetyt toteutukset hakemistosta
// dist/ vapaassa portissa. Osoite välitetään testeille ympäristö-
// muuttujassa, joten kiinteää porttia ei tarvita.
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { extname, join, normalize } from "node:path";

const TYYPIT: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
};
const JUURI = join(import.meta.dirname, "..", "dist");

export default async function kaynnista(): Promise<() => Promise<void>> {
  const palvelin = createServer((pyynto, vastaus) => {
    const polku = normalize(decodeURIComponent(
      new URL(pyynto.url ?? "/", "http://x").pathname));
    const tiedosto = join(JUURI, polku.endsWith("/")
      ? polku + "index.html" : polku);
    readFile(tiedosto).then((sisalto) => {
      vastaus.writeHead(200, {
        "content-type": TYYPIT[extname(tiedosto)] ?? "text/plain",
      });
      vastaus.end(sisalto);
    }, () => { vastaus.writeHead(404).end("ei löydy"); });
  });
  await new Promise<void>((valmis) =>
    palvelin.listen(0, "127.0.0.1", valmis));
  const { port } = palvelin.address() as AddressInfo;
  process.env.SOVELLUKSET = `http://127.0.0.1:${port}`;
  return () => new Promise((valmis) => palvelin.close(() => valmis()));
}
