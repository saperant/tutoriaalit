// Tilausrajapinta, jossa on OWASP API Top 10:n kolme yleisintä
// valtuutusvirhettä: objektitason (BOLA/IDOR), funktiotason ja
// ominaisuustason (massamääritys) puuttuva tarkistus.
import { type Kasittelija, type Pyynto, json } from "../http.ts";

type Kayttaja = { nimi: string; rooli: "asiakas" | "yllapitaja";
                  sahkoposti: string };
type Tilaus = { id: number; omistaja: string; summa: number };

// Yksinkertaistus: token on suoraan käyttäjän nimi. Oikea tunnistus
// on luvuissa 5–9; tässä luvussa keskitytään valtuutukseen.
function kuka(p: Pyynto, kayttajat: Map<string, Kayttaja>):
    Kayttaja | undefined {
  return kayttajat.get((p.otsakkeet.authorization ?? "").slice(7));
}

export function api(korjattu: boolean): Kasittelija {
  const kayttajat = new Map<string, Kayttaja>([
    ["aino", { nimi: "aino", rooli: "asiakas", sahkoposti: "a@x.fi" }],
    ["ville", { nimi: "ville", rooli: "asiakas", sahkoposti: "v@x.fi" }],
    ["paula", { nimi: "paula", rooli: "yllapitaja", sahkoposti: "p@x.fi" }],
  ]);
  const tilaukset: Tilaus[] = [
    { id: 1, omistaja: "aino", summa: 89 },
    { id: 2, omistaja: "ville", summa: 1299 },
  ];

  // @alku politiikka
  // Kaikki päätökset yhdessä paikassa: kuka saa tehdä mitä millekin.
  const saa = {
    lukeaTilaus: (k: Kayttaja, t: Tilaus) =>
      t.omistaja === k.nimi || k.rooli === "yllapitaja",
    poistaaTilauksen: (k: Kayttaja) => k.rooli === "yllapitaja",
  };
  // @loppu politiikka

  return (p) => {
    const k = kuka(p, kayttajat);
    if (!k) return json({ virhe: "kirjaudu" }, 401);
    const id = Number(p.polku.split("/")[2]);
    const tilaus = tilaukset.find((t) => t.id === id);

    // @alku bola
    if (p.metodi === "GET" && p.polku.startsWith("/tilaukset/")) {
      if (!tilaus) return json({ virhe: "ei löydy" }, 404);
      if (korjattu && !saa.lukeaTilaus(k, tilaus)) {
        // 404 eikä 403: ei paljasteta, että tilaus on olemassa.
        return json({ virhe: "ei löydy" }, 404);
      }
      return json(tilaus);
    }
    // @loppu bola
    // @alku funktiotaso
    if (p.metodi === "DELETE" && p.polku.startsWith("/tilaukset/")) {
      // Haavoittuva versio luottaa siihen, ettei asiakkaan käyttöliittymä
      // näytä poistopainiketta.
      if (korjattu && !saa.poistaaTilauksen(k)) {
        return json({ virhe: "kielletty" }, 403);
      }
      tilaukset.splice(tilaukset.findIndex((t) => t.id === id), 1);
      return { tila: 204 };
    }
    // @loppu funktiotaso
    // @alku massamaaritys
    if (p.metodi === "PATCH" && p.polku === "/oma") {
      const muutos = JSON.parse(p.runko) as Record<string, unknown>;
      if (korjattu) {
        // Sallittujen kenttien luettelo: vain sähköposti on muutettavissa.
        if (typeof muutos.sahkoposti === "string") {
          k.sahkoposti = muutos.sahkoposti;
        }
      } else {
        Object.assign(k, muutos);               // VÄÄRIN: myös rooli
      }
      return json(k);
    }
    // @loppu massamaaritys
    return json({ virhe: "ei löydy" }, 404);
  };
}
