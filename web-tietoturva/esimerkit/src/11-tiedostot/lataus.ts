// Tiedostojen lataus palveluun ja jakelu takaisin selaimelle.
import { randomUUID } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import type { Kasittelija, Vastaus } from "../http.ts";

// @alku tunnistus
// Tiedoston tyyppi päätellään sisällön alusta (taikaluvut), ei nimestä
// eikä asiakkaan ilmoittamasta Content-Typestä.
const TYYPIT: [string, Buffer][] = [
  ["image/png", Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a])],
  ["image/jpeg", Buffer.from([0xff, 0xd8, 0xff])],
  ["application/pdf", Buffer.from("%PDF-")],
];

export function tyyppi(data: Buffer): string | undefined {
  return TYYPIT.find(([, alku]) =>
    data.subarray(0, alku.length).equals(alku))?.[0];
}
// @loppu tunnistus

export function lataukset(hak: string, korjattu: boolean): Kasittelija {
  const tiedot = new Map<string, string>();         // id -> tyyppi
  return async (p): Promise<Vastaus> => {
    const data = p.raaka;
    // @alku haavoittuva
    if (!korjattu && p.metodi === "POST") {
      const nimi = p.haku.get("nimi") ?? "";        // VÄÄRIN: käyttäjän nimi
      await writeFile(path.join(hak, nimi), data);
      return { tila: 201, runko: `/tiedostot/${nimi}` };
    }
    if (!korjattu) {
      const nimi = decodeURIComponent(p.polku.slice("/tiedostot/".length));
      const tyyppi = nimi.endsWith(".html") ? "text/html" : "image/png";
      return { otsakkeet: { "Content-Type": tyyppi },
               runko: await readFile(path.join(hak, nimi)) };
    }
    // @loppu haavoittuva
    // @alku korjattu
    if (p.metodi === "POST") {
      if (data.length > 5 * 1024 * 1024) return { tila: 413 };
      const t = tyyppi(data);
      if (!t) return { tila: 415, runko: "sallitut: PNG, JPEG, PDF" };
      const id = randomUUID();                       // palvelimen nimi
      await mkdir(path.join(hak, "lataukset"), { recursive: true });
      await writeFile(path.join(hak, "lataukset", id), data);
      tiedot.set(id, t);
      return { tila: 201, runko: `/tiedostot/${id}` };
    }
    const id = p.polku.slice("/tiedostot/".length);
    const t = tiedot.get(id);                        // vain tunnetut id:t
    if (!t) return { tila: 404 };
    return { otsakkeet: {
      "Content-Type": t,
      "Content-Disposition": "attachment",
      "X-Content-Type-Options": "nosniff",
      "Content-Security-Policy": "sandbox; default-src 'none'",
    }, runko: await readFile(path.join(hak, "lataukset", id)) };
    // @loppu korjattu
  };
}
