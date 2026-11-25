# Johdanto {.runko-johdanto}

SQL on relaatiotietokantojen kyselykieli. Sillä määritellään tietojen
rakenne, haetaan ja muutetaan tietoja ja hallitaan transaktioita. SQL on
*deklaratiivinen*: kysely kertoo, millaisen tuloksen halutaan, ei sitä,
miten se lasketaan. Tietokannan kyselyoptimoija valitsee
suoritustavan, kuten käytettävät indeksit ja liitosjärjestyksen.

Tavoitteena ei ole luetella syntaksia vaan opettaa, miten
ammattilaiset mallintavat tietoa, kirjoittavat oikein toimivia ja
tehokkaita kyselyitä ja käyttävät tietokantaa sovelluksesta.

## Esitiedot ja rajaus

Tutoriaali olettaa, että lukija osaa ohjelmoida (taito *Ohjelmoinnin
perusteet (Python)*); sovelluslukujen esimerkit ovat Pythonia. Muut kuin
relaatiotietokannat käsittelee taito *NoSQL-tietokannat* ja
tietokantakoodin testauksen oikealla palvelimella taito
*Integraatiotestaus ja Testcontainers*.

## Historia ja standardit

Edgar F. Codd esitti relaatiomallin IBM:llä vuonna 1970. Mallissa tieto
on relaatioina eli tauluina, ja kyselyt ovat joukko-operaatioita, jotka
eivät riipu tietojen fyysisestä tallennustavasta. IBM:n System R
-projekti kehitti 1970-luvulla mallille kielen SEQUEL, josta tuli SQL.
Ensimmäiset kaupalliset toteutukset olivat Oracle (1979) ja IBM:n DB2.

SQL on ISO- ja ANSI-standardi vuodesta 1986–87. Tärkeimmät versiot:

| Standardi | Keskeiset lisäykset |
|-----------|---------------------|
| SQL-92 | `JOIN`-syntaksi, `CASE`, eristystasot |
| SQL:1999 | rekursiiviset kyselyt (`WITH RECURSIVE`), triggerit |
| SQL:2003 | ikkunafunktiot, `MERGE` |
| SQL:2011 | aikaversioidut taulut |
| SQL:2016 | JSON-funktiot, rivihahmojen tunnistus |
| SQL:2023 | ominaisuusgraafikyselyt (SQL/PGQ), JSON-tyyppi |

Mikään tietokanta ei toteuta standardia kokonaan, ja jokaisella on omia
laajennuksiaan. Ydin on silti yhteinen: tämän tutoriaalin kyselyt
toimivat pienin muutoksin PostgreSQL:ssä, MySQL:ssä ja SQL Serverissä.

## Mihin relaatiotietokanta sopii ja mihin ei

Relaatiotietokanta on oletusvalinta lähes kaikkeen liiketoimintadataan:
asiakkaat, tilaukset, kirjanpito, varastot ja käyttäjät. Sen vahvuudet
ovat eheyssäännöt, transaktiot ja vapaat kyselyt: uusi raportti ei vaadi
uutta tallennusrakennetta.

Muut ratkaisut ovat perusteltuja, kun

- tietoa kirjoitetaan niin paljon, ettei yksi palvelin riitä, ja
  saatavuus on tärkeämpää kuin vahva yhtenäisyys (hajautetut
  avain–arvo- ja saraketietokannat; taito *Hajautetut järjestelmät*)
- tarvitaan täystekstihakua suuresta dokumenttijoukosta (hakukoneet)
- analytiikka käy läpi miljardeja rivejä (sarakepohjaiset tietovarastot
  kuten DuckDB ja ClickHouse, joissa kyselykieli on silti SQL)
- tieto on pelkkiä välimuistiin tallennettuja avain–arvo-pareja.

Yleinen virhe on valita dokumenttitietokanta siksi, että skeematon
tallennus tuntuu alussa joustavalta. Skeema on silloin olemassa
sovelluskoodissa, jossa sen eheyttä ei valvo kukaan. Avain-arvo-,
dokumentti-, leveäsarake- ja graafitietokannat esitellään taidossa
*NoSQL-tietokannat*, ja aikasarjoja käsitellään luvussa 13.

## Toteutukset ja tämän tutoriaalin valinta

Yleisimmät relaatiotietokannat ovat PostgreSQL, MySQL ja MariaDB,
SQLite, Microsoft SQL Server ja Oracle. PostgreSQL on avoimista
palvelintietokannoista monipuolisin ja yleinen oletusvalinta uusiin
projekteihin.

Tutoriaalin esimerkit ajetaan **SQLite 3.45:llä**. Perusteet:

- SQLite on kirjasto, ei palvelin. Tietokanta on yksi tiedosto tai pelkkä
  muistialue, joten esimerkki ajetaan ilman asennuksia, käyttäjiä tai
  yhteysasetuksia.
- SQL:n ydin on sama: liitokset, koosteet, alikyselyt, CTE:t,
  ikkunafunktiot, `RETURNING`, `UPSERT` ja transaktiot toimivat kuten
  PostgreSQL:ssä.
- SQLite on maailman levinnein tietokanta. Se on jokaisessa
  älypuhelimessa ja selaimessa ja sopii sovelluksen omaksi
  tietokannaksi, testeihin ja tiedostomuodoksi.

Luvut 12–15 ajavat esimerkkejä myös oikeilla PostgreSQL- ja
MariaDB-palvelimilla. Erot PostgreSQL:ään kerrotaan jo aiemmin siellä,
missä ne vaikuttavat. Olennaisimmat:

| Asia | SQLite 3.45 | PostgreSQL |
|------|-------------|------------|
| Arkkitehtuuri | kirjasto, tietokanta tiedostossa | palvelin, verkkoyhteys |
| Tyypit | tyyppi on arvolla; `STRICT` pakottaa | tiukka, laaja tyyppivalikoima |
| Päivämäärät | ISO 8601 -teksti ja funktiot | `date`, `timestamptz`, `interval` |
| Totuusarvot | kokonaisluvut 0 ja 1 | `boolean` |
| Viiteavaimet | oletuksena pois päältä | aina voimassa |
| Samanaikaisuus | yksi kirjoittaja kerrallaan | monta kirjoittajaa (MVCC) |
| Eristystaso | aina sarjallistuva | oletuksena *read committed* |
| Kyselysuunnitelma | `EXPLAIN QUERY PLAN` | `EXPLAIN (ANALYZE)` |
| Skeemamuutokset | `ALTER TABLE` rajoitettu | kattava, transaktioissa |

Molemmissa on `RETURNING`, `ON CONFLICT`, ikkunafunktiot, `FILTER` ja
rekursiiviset CTE:t.

## Työkalut

SQLiten komentorivityökalu `sqlite3` ajaa SQL-lauseita ja
pistekomentoja, jotka eivät ole SQL:ää vaan työkalun asetuksia:

| Komento | Tarkoitus |
|---------|-----------|
| `sqlite3 kauppa.db` | avaa tai luo tietokantatiedoston |
| `.mode box`, `.headers on` | taulukkomuotoinen tuloste otsikkoineen |
| `.nullvalue NULL` | näyttää NULL-arvot näkyvästi |
| `.schema tilaus` | näyttää taulun määrittelyn |
| `.read tiedosto.sql` | ajaa tiedoston |
| `.eqp on`, `.timer on` | kyselysuunnitelma ja ajoaika jokaisesta kyselystä |

Graafisista työkaluista DB Browser for SQLite ja DBeaver tukevat
SQLiteä; DBeaver ja `psql` toimivat myös PostgreSQL:n kanssa.

## Ensimmäinen tietokanta

Esimerkki tallentaa lämpötilamittauksia ja laskee niistä yhteenvedon
anturikohtaisesti:

```{.sql tiedosto="esimerkit/01-ensimmainen.sql"}
```

Ajo komennolla `sqlite3 -bail -batch -init 01-ensimmainen.sql :memory:
.quit` tulostaa:

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

Jo tässä näkyy kolme toistuvaa käytäntöä: taulu on `STRICT`, jolloin
SQLite tarkistaa sarakkeiden tyypit, aikaleimat ovat ISO 8601
-muodossa, joka järjestyy oikein merkkijonona, ja tulosteen järjestys on
määrätty `ORDER BY` -lauseella. Ilman sitä rivien järjestys ei ole
taattu.

## Tutoriaalin rakenne

Tutoriaali etenee viidessä osassa, ja kukin osa nojaa edellisiin:

| Luvut | Osa | Kysymys |
|-------|-----|---------|
| 2 | tietomalli | miten tieto jaetaan tauluihin |
| 3–8 | kyselyt | miten tauluista kysytään |
| 9–11 | eheys, muutokset ja suorituskyky | miten tieto pysyy oikeana ja kyselyt nopeina |
| 12–13 | järjestelmät ja aikasarjat | miten tietokannat eroavat ja miten ne taipuvat mittausdataan |
| 14–15 | sovellus | miten tietokantaa käytetään ohjelmakoodista |

Luvut 2–11 ovat tietokannasta riippumatonta SQL:ää, ja ne kannattaa
lukea järjestyksessä. Luvut 12–13 ja 14–15 voi lukea kummassa
järjestyksessä tahansa.

## Tutoriaalin tietomalli

Luvusta 2 alkaen esimerkit käyttävät pientä verkkokauppaa: asiakkaat,
tuotteet, tilaukset ja tilausrivit. Jokainen esimerkki luo skeeman ja
datan alussa uudelleen, koska esimerkit ajetaan toisistaan erillään.
Tekstissä skeemaa ei toisteta, vaan näytetään vain luvun asia.

## Esimerkkien testaus

Kaikki tutoriaalin koodi on peräisin hakemiston `esimerkit`
tiedostoista. SQL-tiedostot ajetaan muistissa olevaan tietokantaan
komennolla `sqlite3 -bail -batch`, ja tulostetta verrataan tiedostoon,
josta myös tekstin tulosteet on poimittu. Valitsin `-bail` lopettaa
ajon ensimmäiseen virheeseen. Esimerkit, jotka näyttävät tarkoituksella
rikotun rajoitteen, testataan varmistamalla, että ajo kaatuu odotettuun
virheeseen.

Python-esimerkit (luvut 10 ja 13–15) tarkistetaan ruffilla ja
`mypy --strict` -tilassa ja ajetaan samalla tavalla. Lukujen 12–15
palvelinesimerkit ajetaan testissä väliaikaisilla PostgreSQL- ja
MariaDB-palvelimilla.
