// TOTP (RFC 6238): aikaan perustuva kertakäyttökoodi, jonka
// todennussovellus ja palvelin laskevat yhteisestä salaisuudesta.
import { createHmac } from "node:crypto";

// @alku totp
export function totp(salaisuus: Buffer, aika: number, numeroita = 6,
                     askel = 30): string {
  const laskuri = Buffer.alloc(8);
  laskuri.writeBigUInt64BE(BigInt(Math.floor(aika / askel)));
  const mac = createHmac("sha1", salaisuus).update(laskuri).digest();
  const i = mac[mac.length - 1]! & 0x0f;          // dynaaminen katkaisu
  const luku = mac.readUInt32BE(i) & 0x7fffffff;
  return String(luku % 10 ** numeroita).padStart(numeroita, "0");
}
// @loppu totp

// @alku tarkistus
// Kellojen erolle sallitaan yksi askel kumpaankin suuntaan. Käytetty
// askel muistetaan, jotta sama koodi ei kelpaa toista kertaa.
export class TotpTarkistin {
  #viimeisin = -1;
  #salaisuus: Buffer;
  constructor(salaisuus: Buffer) { this.#salaisuus = salaisuus; }

  tarkista(koodi: string, aika: number): boolean {
    const nyt = Math.floor(aika / 30);
    for (const askel of [nyt - 1, nyt, nyt + 1]) {
      if (askel > this.#viimeisin &&
          totp(this.#salaisuus, askel * 30) === koodi) {
        this.#viimeisin = askel;
        return true;
      }
    }
    return false;
  }
}
// @loppu tarkistus
