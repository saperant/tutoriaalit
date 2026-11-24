# Valtuutus rajapinnoissa

Tunnistus kertoo, kuka käyttäjä on; valtuutus päättää, mitä hän saa
tehdä. *Tietoturvan perusteet* esitteli pääsynhallinnan mallit (RBAC,
ABAC). Tämä luku käsittelee niitä virheitä, jotka johtavat OWASP:n
API-listan kärkeen: valtuutus puuttuu yksittäisestä objektista,
toiminnosta tai kentästä.

## Kolme tasoa

| Taso | Virhe | Esimerkki |
|------|-------|-----------|
| Objekti (BOLA, IDOR) | tunnistettu käyttäjä pääsee *toisen* käyttäjän objektiin | `/tilaukset/2` numeroa vaihtamalla |
| Toiminto | asiakas kutsuu ylläpidon toimintoa | `DELETE /tilaukset/2` ilman roolia |
| Ominaisuus | käyttäjä muuttaa kenttää, jota ei saisi (massamääritys) | `{"rooli": "yllapitaja"}` profiilin päivityksessä |

Kaikissa kolmessa käyttöliittymä on yleensä kunnossa: se ei näytä
toisen tilausta, poistopainiketta eikä roolikenttää. Rajapinta
kuitenkin luottaa siihen, ettei kukaan kutsu sitä suoraan.

## Politiikka yhdessä paikassa

Valtuutuspäätökset kootaan yhteen paikkaan funktioiksi, jotka saavat
käyttäjän ja kohteen. Koodissa näkyy silloin, mitä tarkistetaan, ja
politiikkaa voi testata erikseen:

```{.typescript tiedosto="esimerkit/src/10-valtuutus/api.ts" osa="politiikka"}
```

Suuremmissa järjestelmissä politiikka voi olla omana kielenään (OPA
ja Rego, Cedar) tai suhdepohjaisena mallina (Zanzibar-tyyppiset
järjestelmät kuten OpenFGA). Periaate on sama: päätös on yhdessä
paikassa, ja sitä kutsutaan jokaisesta rajapinnasta.

## Objektitaso

Tarkistus tehdään joka kerta, kun objekti haetaan tunnisteella.
Satunnainen UUID ei korvaa tarkistusta: tunnisteet vuotavat
lokeihin, linkkeihin ja muihin rajapintoihin.

```{.typescript tiedosto="esimerkit/src/10-valtuutus/api.ts" osa="bola"}
```

Vastaus on 404 eikä 403, jotta rajapinta ei paljasta, onko toisen
käyttäjän tilaus olemassa. Vielä parempi on hakea tietokannasta
suoraan käyttäjän rajaamana (`WHERE id = ? AND omistaja = ?`), jolloin
tarkistusta ei voi unohtaa myöhemmässä koodissa.

## Toimintotaso

```{.typescript tiedosto="esimerkit/src/10-valtuutus/api.ts" osa="funktiotaso"}
```

Kehyksissä toimintotaso merkitään yleensä reitin yhteyteen
(`@PreAuthorize`, välikerros reitille). Oletuksen on oltava
kielteinen: reitti ilman merkintää on suljettu, ei avoin.

## Ominaisuustaso

Massamääritys syntyy, kun pyynnön runko kopioidaan sellaisenaan
olioon tai tietokantariviin (`Object.assign`, ORM:n `update(body)`).
Korjaus on sallittujen kenttien luettelo tai erillinen syöteolio
(DTO), jossa muutettavissa olevat kentät ovat ainoat kentät:

```{.typescript tiedosto="esimerkit/src/10-valtuutus/api.ts" osa="massamaaritys"}
```

Sama koskee vastauksia: olio sarjallistetaan vastaukseksi rajatun
vastausolion kautta, jotta salasanatiiviste tai sisäiset kentät
eivät vuoda (*excessive data exposure*).

## Testit

```{.typescript tiedosto="esimerkit/src/10-valtuutus/valtuutus.test.ts" osa="testit"}
```

Valtuutustestit kirjoitetaan **toisen käyttäjän näkökulmasta**: jokaiselle
rajapinnalle vähintään yksi testi, jossa väärä käyttäjä yrittää.
Taulukkotesti, jossa ovat roolit ja rajapinnat ja odotettu tila
jokaisessa solussa, löytää puuttuvat tarkistukset järjestelmällisesti.

## Käytännössä

- **Oletuksena kielletty.** Jokainen reitti ja objekti vaatii
  myönteisen päätöksen.
- **Politiikka yhdessä paikassa**, ja sitä kutsutaan joka
  rajapinnasta. Käyttöliittymän piilottama painike ei ole tarkistus.
- **Rajaa kysely käyttäjään**, älä tarkista jälkikäteen.
- **Syöte- ja vastausoliot** rajaavat kentät molempiin suuntiin.
- **Hinta:** objektitason tarkistus on yksi ehto kyselyssä; politiikan
  keskittäminen maksaa hieman suunnittelua alussa ja säästää
  tietomurron selvittämisen.

## Itsearviointi

- Osaat erottaa objekti-, toiminto- ja ominaisuustason
  valtuutusvirheet ja antaa kustakin esimerkin.
- Osaat keskittää valtuutuspolitiikan ja kutsua sitä rajapinnoista.
- Osaat estää massamäärityksen ja liian laajat vastaukset.
- Osaat kirjoittaa valtuutustestit toisen käyttäjän näkökulmasta.
