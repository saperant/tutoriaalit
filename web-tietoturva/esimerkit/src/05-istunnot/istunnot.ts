// Istuntojen hallinta: satunnaiset tunnisteet, vanheneminen,
// kierto kirjautuessa ja mitätöinti uloskirjautuessa.
import { randomBytes } from "node:crypto";
import { type Kasittelija, type Pyynto, lomake } from "../http.ts";

// @alku varasto
type Istunto = { kayttaja?: string; luotu: number; kaytetty: number };

export class Istunnot {
  #istunnot = new Map<string, Istunto>();
  #kello: () => number;
  #joutoaika: number;
  #enimmaisika: number;

  constructor(kello: () => number = Date.now,
              joutoaika = 15 * 60_000,           // 15 min
              enimmaisika = 8 * 3600_000) {      // 8 h
    this.#kello = kello;
    this.#joutoaika = joutoaika;
    this.#enimmaisika = enimmaisika;
  }

  luo(kayttaja?: string): string {
    const id = randomBytes(32).toString("base64url");  // 256 bittiä
    const nyt = this.#kello();
    this.#istunnot.set(id, { kayttaja, luotu: nyt, kaytetty: nyt });
    return id;
  }

  hae(id: string): Istunto | undefined {
    const i = this.#istunnot.get(id);
    const nyt = this.#kello();
    if (i && (nyt - i.kaytetty > this.#joutoaika ||
              nyt - i.luotu > this.#enimmaisika)) {
      this.#istunnot.delete(id);                  // vanhentunut
      return undefined;
    }
    if (i) i.kaytetty = nyt;
    return i;
  }

  // Kirjautuminen ja oikeuksien muutos saavat aina uuden tunnisteen.
  kierra(vanha: string, kayttaja: string): string {
    this.#istunnot.delete(vanha);
    return this.luo(kayttaja);
  }

  poista(id: string): void { this.#istunnot.delete(id); }
}
// @loppu varasto

// @alku eväste
export const EVASTE = "__Host-sid";
export function evaste(id: string): string {
  return `${EVASTE}=${id}; Path=/; Secure; HttpOnly; SameSite=Lax`;
}
// @loppu eväste

// Palvelu, jossa kirjautumisen jälkeen näkyy käyttäjän nimi.
export function palvelu(korjattu: boolean, istunnot = new Istunnot()):
    Kasittelija {
  const tunnus = (p: Pyynto) =>
    p.evasteet.get(EVASTE) ??
    (korjattu ? undefined : p.haku.get("sid") ?? undefined);

  return (p) => {
    const id = tunnus(p) ?? "";
    // @alku kirjaudu
    if (p.metodi === "POST" && p.polku === "/kirjaudu") {
      const kayttaja = lomake(p).get("tunnus") ?? "";  // (salasana: luku 6)
      let uusi: string;
      if (korjattu) {
        uusi = istunnot.kierra(id, kayttaja);
      } else {
        // VÄÄRIN: olemassa oleva tunniste saa kirjautuneen käyttäjän.
        uusi = istunnot.hae(id) ? id : istunnot.luo();
        istunnot.hae(uusi)!.kayttaja = kayttaja;
      }
      return { tila: 204, otsakkeet: { "Set-Cookie": evaste(uusi) } };
    }
    // @loppu kirjaudu
    if (p.metodi === "POST" && p.polku === "/ulos") {
      istunnot.poista(id);
      return { tila: 204, otsakkeet: { "Set-Cookie":
        `${EVASTE}=; Path=/; Secure; HttpOnly; Max-Age=0` } };
    }
    if (p.polku === "/uusi") {                   // anonyymi istunto
      return { runko: istunnot.luo() };
    }
    const kayttaja = istunnot.hae(id)?.kayttaja;
    return kayttaja ? { runko: `Hei ${kayttaja}` }
                    : { tila: 401, runko: "Kirjaudu" };
  };
}
