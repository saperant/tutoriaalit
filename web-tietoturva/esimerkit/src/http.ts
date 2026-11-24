// Pieni HTTP-kehys esimerkkien palvelimille: reititys, evästeet,
// lomakkeet ja JSON. Tarkoitus on pitää jokainen tietoturvapäätös
// näkyvissä esimerkin omassa koodissa eikä kehyksen sisällä.
import http from "node:http";
import type { AddressInfo } from "node:net";

export type Pyynto = {
  metodi: string;
  polku: string;
  haku: URLSearchParams;
  otsakkeet: http.IncomingHttpHeaders;
  evasteet: Map<string, string>;
  runko: string;
  raaka: Buffer;                // runko tavuina (tiedostot)
  osoite: string;               // asiakkaan IP-osoite
};

export type Vastaus = {
  tila?: number;
  otsakkeet?: Record<string, string | string[]>;
  runko?: string | Buffer;
};

export type Kasittelija = (p: Pyynto) => Vastaus | Promise<Vastaus>;

export type Palvelin = { url: string; sulje: () => Promise<void> };

// @alku evasteet
export function lueEvasteet(otsake: string | undefined):
    Map<string, string> {
  const tulos = new Map<string, string>();
  for (const osa of (otsake ?? "").split(";")) {
    const i = osa.indexOf("=");
    if (i > 0) tulos.set(osa.slice(0, i).trim(), osa.slice(i + 1).trim());
  }
  return tulos;
}
// @loppu evasteet

export function lomake(p: Pyynto): URLSearchParams {
  return new URLSearchParams(p.runko);
}

export function json(data: unknown, tila = 200): Vastaus {
  return {
    tila,
    otsakkeet: { "Content-Type": "application/json; charset=utf-8" },
    runko: JSON.stringify(data),
  };
}

export function html(sivu: string, otsakkeet: Record<string, string> = {}):
    Vastaus {
  return {
    otsakkeet: { "Content-Type": "text/html; charset=utf-8", ...otsakkeet },
    runko: sivu,
  };
}

// Escapoi tekstin HTML-elementin sisältöön tai lainausmerkeissä
// olevaan attribuuttiin. Muihin konteksteihin (URL, JavaScript, CSS)
// tarvitaan oma koodaus, ks. luku 3.
export function h(teksti: string): string {
  return teksti.replace(/[&<>"']/g, (m) => `&#${m.charCodeAt(0)};`);
}

export async function kaynnista(kasittelija: Kasittelija,
                                isanta = "127.0.0.1"): Promise<Palvelin> {
  const palvelin = http.createServer(async (req, res) => {
    const osat: Buffer[] = [];
    for await (const osa of req) osat.push(osa as Buffer);
    const url = new URL(req.url ?? "/", "http://x");
    const pyynto: Pyynto = {
      metodi: req.method ?? "GET",
      polku: url.pathname,
      haku: url.searchParams,
      otsakkeet: req.headers,
      evasteet: lueEvasteet(req.headers.cookie),
      runko: Buffer.concat(osat).toString("utf8"),
      raaka: Buffer.concat(osat),
      osoite: req.socket.remoteAddress ?? "",
    };
    try {
      const v = await kasittelija(pyynto);
      res.writeHead(v.tila ?? 200, v.otsakkeet ?? {});
      res.end(v.runko ?? "");
    } catch (virhe) {
      // Sisäistä virhettä ei paljasteta asiakkaalle (luku 11).
      console.error(virhe);
      res.writeHead(500, { "Content-Type": "text/plain" });
      res.end("Sisäinen virhe");
    }
  });
  await new Promise<void>((ok) => palvelin.listen(0, isanta, ok));
  const { port } = palvelin.address() as AddressInfo;
  return {
    url: `http://${isanta}:${port}`,
    sulje: () => new Promise<void>((ok) => {
      palvelin.closeAllConnections();
      palvelin.close(() => ok());
    }),
  };
}
