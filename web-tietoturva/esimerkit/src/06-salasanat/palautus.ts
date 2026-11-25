// Salasanan palautus: kertakäyttöinen, vanheneva token, josta palvelin
// tallentaa vain tiivisteen.
import { createHash, randomBytes } from "node:crypto";

// @alku palautus
type Pyynto = { kayttaja: string; vanhenee: number };

const tiiviste = (token: string) =>
  createHash("sha256").update(token).digest("hex");

export class Palautus {
  #pyynnot = new Map<string, Pyynto>();     // tokenin tiiviste -> pyyntö
  #kayttajat: Set<string>;
  #kello: () => number;
  #voimassa: number;

  constructor(kayttajat: Iterable<string>, kello: () => number = Date.now,
              voimassa = 30 * 60_000) {     // 30 min
    this.#kayttajat = new Set(kayttajat);
    this.#kello = kello;
    this.#voimassa = voimassa;
  }

  // Palauttaa tokenin, joka lähetetään käyttäjän sähköpostiin, tai
  // undefined, jos tunnusta ei ole. Selaimelle vastataan kummassakin
  // tapauksessa samoin (ks. Käyttäjätunnusten arvailu).
  pyyda(kayttaja: string): string | undefined {
    if (!this.#kayttajat.has(kayttaja)) return undefined;
    for (const [avain, p] of this.#pyynnot) {   // uusi mitätöi vanhat
      if (p.kayttaja === kayttaja) this.#pyynnot.delete(avain);
    }
    const token = randomBytes(32).toString("base64url");   // 256 bittiä
    this.#pyynnot.set(tiiviste(token),
      { kayttaja, vanhenee: this.#kello() + this.#voimassa });
    return token;
  }

  // Palauttaa käyttäjän, jonka salasanan saa nyt vaihtaa.
  kayta(token: string): string | undefined {
    const avain = tiiviste(token);
    const p = this.#pyynnot.get(avain);
    this.#pyynnot.delete(avain);                // kertakäyttöinen
    if (!p || this.#kello() > p.vanhenee) return undefined;
    return p.kayttaja;
  }
}
// @loppu palautus
