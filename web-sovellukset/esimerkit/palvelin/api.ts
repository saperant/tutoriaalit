// Pieni kehitys- ja testipalvelin pelkällä Noden http-modulilla. Ajo:
//   node palvelin/api.ts          (portti 3001)
import { createServer, type IncomingMessage } from "node:http";
import type { AddressInfo } from "node:net";
import { validoi, type Luonnos } from "../src/05-lomakkeet/varaus.ts";
import { TILAT } from "../src/tilat.ts";

// @alku palvelin
type Vastaus = { status: number; runko: unknown };

async function lueJson(pyynto: IncomingMessage): Promise<unknown> {
  let teksti = "";
  for await (const pala of pyynto) {
    teksti += String(pala);
    if (teksti.length > 10_000) throw new Error("liian suuri pyyntö");
  }
  return JSON.parse(teksti);
}

export function luoPalvelin(tanaan: () => string) {
  const varaukset: (Luonnos & { id: string })[] = [];

  async function kasittele(p: IncomingMessage): Promise<Vastaus> {
    const polku = new URL(p.url ?? "/", "http://x").pathname;
    if (p.method === "GET" && polku === "/api/tilat") {
      return { status: 200, runko: TILAT };
    }
    const osuma = /^\/api\/tilat\/([\w-]+)$/.exec(polku);
    if (p.method === "GET" && osuma) {
      const tila = TILAT.find((t) => t.id === osuma[1]);
      return tila ? { status: 200, runko: tila }
                  : { status: 404, runko: { virhe: "Tilaa ei löydy." } };
    }
    if (p.method === "POST" && polku === "/api/varaukset") {
      const l = (await lueJson(p)) as Luonnos;   // tarkistetaan alla
      const virheet = validoi(l, tanaan());
      if (Object.keys(virheet).length > 0) {
        return { status: 422, runko: { virhe: "Virheellinen varaus.",
                                       virheet } };
      }
      if (varaukset.some((v) => v.tilaId === l.tilaId &&
                                v.paiva === l.paiva && v.alku === l.alku)) {
        return { status: 409, runko: { virhe: "Tila on jo varattu." } };
      }
      const id = `v${varaukset.length + 1}`;
      varaukset.push({ ...l, id });
      return { status: 201, runko: { id } };
    }
    return { status: 404, runko: { virhe: "Tuntematon osoite." } };
  }

  return createServer((pyynto, vastaus) => {
    kasittele(pyynto)
      .catch(() => ({ status: 400,
                      runko: { virhe: "Virheellinen pyyntö." } }))
      .then(({ status, runko }) => {
        vastaus.writeHead(status, { "Content-Type": "application/json" });
        vastaus.end(JSON.stringify(runko));
      });
  });
}
// @loppu palvelin

export async function kaynnista(portti = 0, tanaan = () => "2026-11-24") {
  const palvelin = luoPalvelin(tanaan);
  await new Promise<void>((ok) => palvelin.listen(portti, "127.0.0.1", ok));
  const { port } = palvelin.address() as AddressInfo;
  return {
    osoite: `http://127.0.0.1:${port}`,
    sulje: () => new Promise<void>((ok) => palvelin.close(() => ok())),
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { osoite } = await kaynnista(3001);
  console.log(`API: ${osoite}/api/tilat`);
}
