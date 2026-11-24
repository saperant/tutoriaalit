// SSRF (server-side request forgery): palvelin hakee käyttäjän antaman
// osoitteen ja pääsee samalla sisäverkkoon, johon hyökkääjä ei yllä.
import { BlockList, isIP } from "node:net";
import { lookup } from "node:dns/promises";

// @alku haavoittuva
export async function esikatseluHaavoittuva(osoite: string):
    Promise<string> {
  const vastaus = await fetch(osoite);              // mikä tahansa kohde
  return (await vastaus.text()).slice(0, 200);
}
// @loppu haavoittuva

// @alku estolista
// Yksityiset, paikalliset ja linkkipaikalliset osoitteet (myös
// pilvipalvelujen metatietopalvelu 169.254.169.254).
export function sisaverkko(): BlockList {
  const b = new BlockList();
  for (const [verkko, pituus] of [["10.0.0.0", 8], ["172.16.0.0", 12],
      ["192.168.0.0", 16], ["127.0.0.0", 8], ["169.254.0.0", 16],
      ["0.0.0.0", 8], ["100.64.0.0", 10]] as const) {
    b.addSubnet(verkko, pituus, "ipv4");
  }
  b.addSubnet("::1", 128, "ipv6");
  b.addSubnet("fc00::", 7, "ipv6");
  b.addSubnet("fe80::", 10, "ipv6");
  return b;
}
// @loppu estolista

// @alku korjattu
export async function esikatselu(osoite: string,
                                 estetyt = sisaverkko()): Promise<string> {
  const url = new URL(osoite);          // jäsennin normalisoi osoitteen
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("vain http ja https");
  }
  const nimi = url.hostname.replace(/^\[|\]$/g, "");
  const ip = isIP(nimi) ? nimi : (await lookup(nimi)).address;
  if (estetyt.check(ip, isIP(ip) === 6 ? "ipv6" : "ipv4")) {
    throw new Error(`kohde ${ip} on estetty`);
  }
  // Uudelleenohjausta ei seurata: muuten julkinen palvelin voisi
  // ohjata pyynnön sisäverkkoon tarkistuksen jälkeen. (Tuotannossa
  // yhteys avataan tarkistettuun IP-osoitteeseen, jotta nimipalvelu
  // ei voi vaihtaa vastausta välissä: DNS rebinding.)
  const vastaus = await fetch(url, { redirect: "manual" });
  if (vastaus.status >= 300 && vastaus.status < 400) {
    throw new Error("uudelleenohjaus estetty");
  }
  return (await vastaus.text()).slice(0, 200);
}
// @loppu korjattu
