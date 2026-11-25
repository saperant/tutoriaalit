# Rajoitteet ja eheys

Rajoite (*constraint*) on sääntö, jonka tietokanta pakottaa jokaisessa
kirjoituksessa. Sovelluksen tarkistukset ovat hyödyllisiä
käyttäjäpalautteeseen, mutta ne eivät riitä: tietokantaan kirjoittavat
myös toiset palvelut, migraatiot, ylläpitoskriptit ja sovelluksen
vanhat versiot, ja samanaikaiset pyynnöt ohittavat sovelluksen
tarkistukset (luku 10). Rajoite on ainoa paikka, jossa sääntö pätee
aina.

| Rajoite | Takaa |
|---------|-------|
| `NOT NULL` | arvo on olemassa |
| `PRIMARY KEY` | rivi on yksilöity |
| `UNIQUE` | arvo tai arvoyhdistelmä on yksikäsitteinen |
| `CHECK (ehto)` | rivi täyttää ehdon |
| `REFERENCES taulu` | viitattu rivi on olemassa |

## Viite-eheys

Viiteavain estää orvot rivit: tilaus ei voi viitata asiakkaaseen, jota
ei ole.

```{.sql tiedosto="esimerkit/09-viiteavain.kaatuu.sql" osa="rikkomus"}
```

```{.tuloste tiedosto="esimerkit/09-viiteavain.virhe"}
```

SQLitessä viiteavaimet tarkistetaan vain, jos yhteydellä on asetettu
`PRAGMA foreign_keys = ON`. Asetus on yhteyskohtainen, eikä sitä
tallenneta tietokantaan, joten sovellus asettaa sen jokaisen yhteyden
avauksen yhteydessä (luku 14). Ilman asetusta yllä oleva lisäys
onnistuisi hiljaa. PostgreSQL tarkistaa viiteavaimet aina.

## CHECK-rajoitteet

`CHECK` ilmaisee arvoalueen tai sarakkeiden välisen säännön.
Tilauksen päivämäärän on oltava kelvollinen:

```{.sql tiedosto="esimerkit/09-check.kaatuu.sql" osa="rikkomus"}
```

```{.tuloste tiedosto="esimerkit/09-check.virhe"}
```

`date('2026-02-30')` palauttaa NULL, joten ehto ei ole tosi. Huomaa
kolmiarvoinen logiikka: `CHECK` hylkää rivin vain, jos ehto on
*epätosi*. Tuntematon kelpaa, minkä vuoksi rajoitteeseen kuuluu myös
`NOT NULL`.

Rajoitteen voi nimetä, jolloin virheilmoitus kertoo säännön nimen:
`CONSTRAINT hinta_ei_negatiivinen CHECK (hinta_snt >= 0)`. Nimetyn
rajoitteen voi PostgreSQL:ssä myös poistaa ja muuttaa nimellä.

## Tyypit ja STRICT

SQLiten tavallisissa tauluissa sarakkeen tyyppi on vain suositus
(*tyyppiaffiniteetti*): arvo tallennetaan muunnettuna, jos muunnos
onnistuu, ja muuten sellaisenaan. `STRICT`-taulu (SQLite 3.37+)
hylkää väärän tyyppiset arvot kuten muut tietokannat:

```{.sql tiedosto="esimerkit/09-strict.kaatuu.sql" osa="joustava"}
```

```{.sql tiedosto="esimerkit/09-strict.kaatuu.sql" osa="tiukka"}
```

```{.tuloste tiedosto="esimerkit/09-strict.odotettu"}
```

```{.tuloste tiedosto="esimerkit/09-strict.virhe"}
```

Ensimmäiseen tauluun päätyi tekstiä kokonaislukusarakkeeseen, ja vika
paljastuisi vasta, kun summa lasketaan väärin. `STRICT`-taulussa
sallitut tyypit ovat `INTEGER`, `REAL`, `TEXT`, `BLOB` ja `ANY`.

## Poistot ja viittaukset

Viiteavaimen toimenpide määrää, mitä viittaaville riveille tapahtuu,
kun viitattu rivi poistetaan:

```{.sql tiedosto="esimerkit/09-poistot.sql" osa="skeema"}
```

```{.sql tiedosto="esimerkit/09-poistot.sql" osa="poisto"}
```

```{.tuloste tiedosto="esimerkit/09-poistot.odotettu"}
```

| Toimenpide | Vaikutus | Käyttö |
|------------|----------|--------|
| `RESTRICT`, `NO ACTION` (oletus) | poisto estetään | itsenäiset oliot: asiakas, tuote |
| `CASCADE` | viittaavat rivit poistetaan | osat: tilausrivi, liite |
| `SET NULL` | viittaus nollataan | valinnainen yhteys |

## Triggerit

Triggeri on lause, jonka tietokanta suorittaa automaattisesti rivin
lisäyksen, muutoksen tai poiston yhteydessä. Tyypillinen käyttö on
muutoshistorian kirjaaminen:

```{.sql tiedosto="esimerkit/09-triggeri.sql" osa="triggeri"}
```

```{.sql tiedosto="esimerkit/09-triggeri.sql" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-triggeri.odotettu"}
```

`old` ja `new` ovat rivin arvot ennen muutosta ja sen jälkeen. Ehto
`WHEN` rajaa triggerin todellisiin muutoksiin. PostgreSQL:ssä triggerin
runko on erillinen funktio (`CREATE FUNCTION ... RETURNS trigger`).

## Käytännössä

- **Säännöt rajoitteiksi.** Jokainen sääntö, jonka voi ilmaista
  rajoitteena, kirjoitetaan rajoitteeksi; sovelluksen validointi on
  lisäksi käyttäjäystävällisiä virheilmoituksia varten. Rajoitteen
  rikkomus käsitellään sovelluksessa virheenä (esim.
  `IntegrityError` → HTTP 409).
- **Viiteavainsarakkeille indeksi.** Poisto ja päivitys viitatussa
  taulussa tarkistavat viittaavat rivit; ilman indeksiä jokainen poisto
  käy koko taulun läpi.
- **`CASCADE` vain osa–kokonaisuus-suhteisiin.** Asiakkaan poisto ei
  saa hävittää kirjanpitoa. Itsenäisille olioille `RESTRICT` ja
  tarvittaessa *pehmeä poisto* (`poistettu` -aikaleima), jonka hinta on,
  että jokainen kysely joutuu rajaamaan poistetut pois.
- **Triggerit säästeliäästi.** Ne sopivat muutoshistoriaan ja
  johdettujen tietojen ylläpitoon, mutta liiketoimintalogiikka
  triggereissä on näkymätöntä sovelluskehittäjälle ja vaikeaa testata.
- **SQLitessä `STRICT` ja `PRAGMA foreign_keys = ON`** aina. Ne tekevät
  SQLitestä tiukkuudeltaan muiden tietokantojen kaltaisen.
- **Hinnat**: rajoitteen tarkistus maksaa hieman jokaisessa
  kirjoituksessa; `UNIQUE` ja pääavain ylläpitävät indeksiä, ja
  viiteavain tekee haun viitattuun tauluun. Hinta on pieni verrattuna
  virheellisen datan korjaamiseen jälkikäteen.

## Itsearviointi

- Osaat valita rajoitteen kuhunkin sääntöön ja perustella, miksi
  pelkkä sovelluksen tarkistus ei riitä.
- Osaat ottaa viiteavaimet ja tiukan tyypityksen käyttöön SQLitessä.
- Osaat valita `RESTRICT`-, `CASCADE`- ja `SET NULL` -toimenpiteen
  yhteyden luonteen mukaan.
- Osaat kirjoittaa muutoshistoriaa kirjaavan triggerin.
