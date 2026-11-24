// Salasanojen tallennus, käytäntö ja vuotaneiden salasanojen tarkistus.
import { createHash, randomBytes, scryptSync, timingSafeEqual }
  from "node:crypto";

// @alku tiiviste
// scrypt on muistia kuluttava tiivistefunktio: arvaaminen on hidasta
// myös näytönohjaimilla. Parametrit tallennetaan tiivisteen mukaan,
// jotta niitä voi myöhemmin kasvattaa.
const N = 2 ** 15, R = 8, P = 1;
const MUISTI = 64 * 1024 * 1024;

export function tiivista(salasana: string): string {
  const suola = randomBytes(16);
  const t = scryptSync(salasana.normalize("NFKC"), suola, 32,
                       { N, r: R, p: P, maxmem: MUISTI });
  return ["scrypt", N, R, P, suola.toString("base64"),
          t.toString("base64")].join("$");
}

export function tarkista(salasana: string, tallennettu: string): boolean {
  const [alg, n, r, p, suola, tiiviste] = tallennettu.split("$");
  if (alg !== "scrypt" || !suola || !tiiviste) return false;
  const odotettu = Buffer.from(tiiviste, "base64");
  const t = scryptSync(salasana.normalize("NFKC"),
                       Buffer.from(suola, "base64"), odotettu.length,
                       { N: Number(n), r: Number(r), p: Number(p),
                         maxmem: MUISTI });
  return timingSafeEqual(t, odotettu);              // vakioaikainen
}
// @loppu tiiviste

// @alku kaytanto
// NIST SP 800-63B (versio 4): pituus ratkaisee, ei merkkiluokat.
// Vähintään 15 merkkiä, kun salasana on ainoa tekijä; vähintään 64
// merkkiä sallittava; ei pakollisia merkkiluokkia eikä määräaikaista
// vaihtoa; tunnetut ja vuotaneet salasanat hylätään.
export function arvioi(salasana: string, tunnus: string,
                       estetyt: Set<string>): string[] {
  const virheet: string[] = [];
  const pituus = [...salasana.normalize("NFKC")].length;
  if (pituus < 15) virheet.push("vähintään 15 merkkiä");
  if (pituus > 128) virheet.push("enintään 128 merkkiä");
  const pienet = salasana.toLowerCase();
  if (estetyt.has(pienet)) virheet.push("yleinen tai vuotanut");
  if (pienet.includes(tunnus.toLowerCase())) {
    virheet.push("sisältää käyttäjätunnuksen");
  }
  return virheet;
}
// @loppu kaytanto

// @alku kanonymiteetti
// Vuotaneiden salasanojen palvelu (esim. Have I Been Pwned) ei saa
// nähdä salasanaa eikä sen tiivistettä. Asiakas lähettää SHA-1-
// tiivisteestä vain viisi ensimmäistä heksamerkkiä ja vertaa
// vastauksena saamiaan loppuosia itse: palvelu näkee vain, että
// salasana on yksi sadoista samalla etuliitteellä alkavista.
export async function vuotanut(salasana: string,
                               palvelu: string): Promise<number> {
  const t = createHash("sha1").update(salasana).digest("hex").toUpperCase();
  const vastaus = await fetch(`${palvelu}/range/${t.slice(0, 5)}`);
  for (const rivi of (await vastaus.text()).split("\n")) {
    const [loppu, maara] = rivi.trim().split(":");
    if (loppu === t.slice(5)) return Number(maara);
  }
  return 0;
}
// @loppu kanonymiteetti
