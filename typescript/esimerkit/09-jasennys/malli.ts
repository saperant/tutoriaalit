// Sovelluksen tyypit johdetaan skeemasta; brändit takaavat, että arvo on
// kulkenut tarkistuksen läpi.
import {
  kokonaisluku, merkkijono, olio, taulukko, tarkenna, type Tyyppi,
} from "./jasennin.ts";

export type Sentit = number & { readonly __brandi: "Sentit" };
export type Sahkoposti = string & { readonly __brandi: "Sahkoposti" };

const onSentit = (n: number): n is Sentit => n >= 0;
const onSahkoposti = (s: string): s is Sahkoposti =>
  /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(s);

const rivi = olio({
  tuote: merkkijono,
  maara: tarkenna(kokonaisluku, (n): n is number => n > 0,
    "määrän on oltava positiivinen"),
  hinta: tarkenna(kokonaisluku, onSentit, "hinta ei voi olla negatiivinen"),
});

export const tilaus = olio({
  asiakas: tarkenna(merkkijono, onSahkoposti, "virheellinen sähköposti"),
  rivit: taulukko(rivi),
});

export type Tilaus = Tyyppi<typeof tilaus>;

export function yhteensa(t: Tilaus): Sentit {
  return t.rivit.reduce((s, r) => s + r.maara * r.hinta, 0) as Sentit;
}
