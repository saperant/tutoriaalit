// Kirjautuminen: käyttäjätunnusten arvailu ja nopeusrajoitus.
import { tiivista, tarkista } from "./salasanat.ts";

// @alku rajoitin
// Merkkiämpäri: jokainen yritys vie merkin, ja merkkejä palautuu
// tasaisesti. Avaimena on sekä tunnus (hidastaa yhden tilin
// arvaamista) että IP-osoite (hidastaa salasanasumutusta).
export class Rajoitin {
  #ampärit = new Map<string, { merkit: number; aika: number }>();
  #koko: number;
  #nopeus: number;                          // merkkiä sekunnissa
  #kello: () => number;

  constructor(koko: number, nopeus: number, kello = Date.now) {
    this.#koko = koko;
    this.#nopeus = nopeus;
    this.#kello = kello;
  }

  salli(avain: string): boolean {
    const nyt = this.#kello();
    const a = this.#ampärit.get(avain) ?? { merkit: this.#koko, aika: nyt };
    a.merkit = Math.min(this.#koko,
                        a.merkit + (nyt - a.aika) / 1000 * this.#nopeus);
    a.aika = nyt;
    this.#ampärit.set(avain, a);
    if (a.merkit < 1) return false;
    a.merkit -= 1;
    return true;
  }
}
// @loppu rajoitin

export type Tulos = { ok: boolean; viesti: string };

export class Kirjautuminen {
  #kayttajat = new Map<string, string>();
  tiivistyksia = 0;                          // testejä varten
  #vale = tiivista("ei-kenenkaan-salasana-123");
  #tunnus = new Rajoitin(5, 1 / 60);         // 5 yritystä, 1/min lisää
  #ip = new Rajoitin(20, 1 / 6);

  constructor(kayttajat: Record<string, string>) {
    for (const [k, s] of Object.entries(kayttajat)) {
      this.#kayttajat.set(k, tiivista(s));
    }
  }

  #tarkista(s: string, t: string): boolean {
    this.tiivistyksia++;
    return tarkista(s, t);
  }

  // @alku haavoittuva
  haavoittuva(tunnus: string, salasana: string): Tulos {
    const t = this.#kayttajat.get(tunnus);
    if (!t) return { ok: false, viesti: "Tuntematon käyttäjä" };
    if (!this.#tarkista(salasana, t)) {
      return { ok: false, viesti: "Väärä salasana" };
    }
    return { ok: true, viesti: "Tervetuloa" };
  }
  // @loppu haavoittuva

  // @alku korjattu
  kirjaudu(tunnus: string, salasana: string, ip: string): Tulos {
    const virhe = { ok: false, viesti: "Väärä tunnus tai salasana" };
    if (!this.#tunnus.salli(`t:${tunnus}`) || !this.#ip.salli(`ip:${ip}`)) {
      return { ok: false, viesti: "Liian monta yritystä, odota hetki" };
    }
    // Tuntemattomallekin tunnukselle lasketaan tiiviste, jotta
    // vastausaika ei paljasta, onko tunnus olemassa.
    const t = this.#kayttajat.get(tunnus);
    const oikein = this.#tarkista(salasana, t ?? this.#vale);
    return t && oikein ? { ok: true, viesti: "Tervetuloa" } : virhe;
  }
  // @loppu korjattu
}
