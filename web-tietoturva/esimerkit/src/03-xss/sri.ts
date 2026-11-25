// Subresource Integrity (SRI): selain ajaa toiselta palvelimelta
// ladatun skriptin vain, jos sen tiiviste vastaa sivun ilmoittamaa.
import { createHash } from "node:crypto";
import { type Kasittelija, html } from "../http.ts";

export const KIRJASTO = "window.kirjasto = 'aito';";

// @alku sri
export function eheys(sisalto: string): string {
  return "sha384-" + createHash("sha384").update(sisalto).digest("base64");
}

// Sivu lataa kirjaston toiselta palvelimelta. integrity-arvo lasketaan
// siitä versiosta, joka on katselmoitu ja testattu.
export function sivu(cdn: string, sri: boolean): Kasittelija {
  const eheysmaaritteet = sri
    ? ` integrity="${eheys(KIRJASTO)}" crossorigin="anonymous"` : "";
  return () => html(`<!doctype html><title>Kauppa</title>
    <script src="${cdn}/kirjasto.js"${eheysmaaritteet}></script>`);
}
// @loppu sri

// "CDN": jakaa kirjaston tai, murrettuna, muutetun version.
export function cdn(murrettu: boolean): Kasittelija {
  return () => ({
    otsakkeet: { "Content-Type": "text/javascript",
                 "Access-Control-Allow-Origin": "*" },
    runko: murrettu ? "window.kirjasto = 'muutettu';" : KIRJASTO,
  });
}
