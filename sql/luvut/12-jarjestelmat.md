# Tietokantajärjestelmät

Edellisten lukujen SQL toimii lähes sellaisenaan kaikissa
relaatiotietokannoissa. Järjestelmät eroavat silti arkkitehtuuriltaan,
ominaisuuksiltaan, lisensseiltään ja yllättävän monelta pieneltä
yksityiskohdalta. Tämä luku esittelee yleisimmät järjestelmät ja näyttää
erot ajamalla saman tehtävän SQLitessä, PostgreSQL 16:ssa ja MariaDB
10.11:ssä. Palvelinesimerkit ajetaan testeissä oikeilla palvelimilla
(skripti `esimerkit/palvelimet/aja.sh`).

## SQLite

SQLite on kirjasto, joka liitetään sovellukseen. Tietokanta on yksi
tiedosto, eikä palvelinta, käyttäjiä tai verkkoyhteyttä ole. Se sopii
sovelluksen omaksi tallennusmuodoksi (mobiilisovellukset, selaimet,
työpöytäohjelmat), sulautettuihin laitteisiin, testeihin ja
tiedostomuodoksi, jota voi kysellä SQL:llä. Kirjoittaja on kerrallaan
yksi, mikä riittää yllättävän pitkälle: WAL-tilassa lukijat eivät
odota kirjoittajaa (luku 10). SQLite on vapaata (*public domain*).

## PostgreSQL

PostgreSQL on avoimista palvelintietokannoista monipuolisin ja yleinen
oletusvalinta uusiin palvelinsovelluksiin. Sen vahvuudet ovat

- **tyypit**: `timestamptz`, `interval`, `numeric`, taulukot, `uuid`,
  välityypit (`tstzrange`) ja `jsonb`, jonka sisältöä voi indeksoida.
  JSONB:n ansiosta PostgreSQL korvaa usein erillisen
  dokumenttitietokannan (taito *NoSQL-tietokannat*).
- **laajennettavuus**: omat tyypit, funktiot ja indeksityypit.
  Laajennuksia ovat esimerkiksi PostGIS (paikkatieto), TimescaleDB
  (aikasarjat, luku 14) ja pgvector (vektorihaku).
- **MVCC** (*multiversion concurrency control*): päivitys kirjoittaa
  rivistä uuden version, ja vanha jää lukijoille, kunnes `VACUUM`
  siivoaa sen. Lukijat ja kirjoittajat eivät estä toisiaan.
- **transaktionaaliset skeemamuutokset** ja kattava standardituki.

Lisenssi on vapaa PostgreSQL-lisenssi. Pilvipalvelut (Amazon RDS ja
Aurora, Google Cloud SQL ja AlloyDB, Azure) tarjoavat sen hallittuna.

## MariaDB ja MySQL

MySQL oli web-sovellusten oletustietokanta LAMP-pinosta (Linux, Apache,
MySQL, PHP) lähtien, ja sitä käyttävät edelleen esimerkiksi WordPress ja
monet suuret verkkopalvelut. MySQL:n alkuperäinen kehittäjä Michael
"Monty" Widenius haarautti MariaDB:n vuonna 2009, kun Oracle osti Sunin
ja sen mukana MySQL:n. Molemmat ovat GPL-lisensoituja; MySQL:llä on
lisäksi Oraclen kaupallinen lisenssi. Versiot ovat sittemmin eronneet:
esimerkiksi MariaDB tukee `INSERT ... RETURNING` -lausetta ja
sekvenssejä, MySQL ei.

Vahvuuksia ovat yksinkertainen ylläpito, nopea lukupainotteinen käyttö,
laaja hosting-tuki ja kypsä replikointi (lähde–replika ja Galera-
klusteri). Tallennus on vaihdettavissa *tallennusmoottoreittain*;
oletus InnoDB on transaktionaalinen ja käyttää MVCC:tä, jossa vanhat
versiot ovat erillisessä *undo-lokissa*.

## Oracle ja SQL Server

Oracle Database ja Microsoftin SQL Server hallitsevat suurten
organisaatioiden järjestelmiä: pankit, vakuutusyhtiöt, julkishallinto ja
toiminnanohjausjärjestelmät. Niiden vahvuudet ovat laajat
yritysominaisuudet (osiointi, salaus, auditointi, varmistus ja palautus
ajankohtaan), Oraclen RAC-klusteri (useampi palvelin samaan
tietokantaan), SQL Serverin integraatio Microsoftin ympäristöön sekä
toimittajan tuki. Molemmilla on oma proseduraalinen kielensä: Oraclessa
PL/SQL ja SQL Serverissä T-SQL. Lisenssit ovat kaupallisia ja
hinnoitellaan prosessoriydinten tai käyttäjien mukaan; ilmaiset
versiot (Oracle Free, SQL Server Express) on rajattu pieniin kantoihin.
Oraclessa tyhjä merkkijono on sama kuin NULL, mikä yllättää muista
järjestelmistä tulevan.

## Muita

- **DuckDB** on SQLiten tapaan sulautettava mutta sarakepohjainen
  tietokanta analytiikkaan: koosteet miljoonista riveistä, Parquet- ja
  CSV-tiedostot suoraan.
- **CockroachDB, YugabyteDB ja Google Spanner** ovat hajautettuja
  SQL-tietokantoja, jotka replikoivat ja osioivat datan useaan
  konesaliin konsensusprotokollalla (taito *Hajautetut järjestelmät*).
  CockroachDB ja YugabyteDB puhuvat PostgreSQL:n protokollaa.
- **IBM Db2** on edelleen yleinen keskuskoneympäristöissä.

## Sama kysely, eri tulos

Murre-erot eivät rajoitu syntaksiin: sama SQL voi ajautua kaikissa ja
antaa eri tuloksen. Seuraava tiedosto ajetaan sellaisenaan kolmessa
järjestelmässä:

```{.sql tiedosto="esimerkit/13-sama.sql" osa="sama"}
```

SQLite:

```{.tuloste tiedosto="esimerkit/13-sama.odotettu"}
```

PostgreSQL:

```{.tuloste tiedosto="esimerkit/palvelimet/13-sama.pg.odotettu"}
```

MariaDB:

```{.tuloste tiedosto="esimerkit/palvelimet/13-sama.maria.odotettu"}
```

- **Jakolasku**: kokonaislukujen jako katkaistaan SQLitessä ja
  PostgreSQL:ssä, MariaDB:ssä tulos on desimaaliluku. Rahalaskut,
  joissa jaetaan, ovat siksi eri järjestelmissä eri suuruisia, ellei
  tyyppiä muunneta itse.
- **Vertailu**: MariaDB:n oletuslajittelujärjestys (*collation*)
  `utf8mb4_general_ci` ei erota isoja ja pieniä kirjaimia (*ci*,
  *case insensitive*) eikä loppuvälilyöntejä. Hakukenttä löytää silloin
  "Aino":n haulla "aino", mutta `UNIQUE`-rajoite estää myös rivit
  "aino" ja "Aino". PostgreSQL ja SQLite vertaavat tavuittain.
- **`||`** yhdistää merkkijonot standardin mukaan, mutta MariaDB:ssä
  ja MySQL:ssä se on looginen TAI; yhdistämiseen käytetään funktiota
  `CONCAT`.
- **NULLin paikka**: PostgreSQL lajittelee NULLit nousevassa
  järjestyksessä viimeisiksi, SQLite ja MariaDB ensimmäisiksi.
  Järjestys kirjoitetaan auki: `ORDER BY x NULLS LAST` (PostgreSQL,
  SQLite) tai `ORDER BY x IS NULL, x` (kaikki).

## Sama tehtävä kolmella murteella

Taulu, jolla on automaattinen avain, rivien lisäys ja palautus,
upsert ja sivutus. SQLite:

```{.sql tiedosto="esimerkit/13-murre.sql" osa="taulu"}
```

PostgreSQL ja MariaDB:

```{.sql tiedosto="esimerkit/palvelimet/13-murre.pg" osa="taulu"}
```

```{.sql tiedosto="esimerkit/palvelimet/13-murre.maria" osa="taulu"}
```

`GENERATED ALWAYS AS IDENTITY` on standardin mukainen automaattinen
avain; PostgreSQL:n vanhempi `serial` tekee saman sekvenssillä.
MariaDB:n `AUTO_INCREMENT` ja SQLiten `INTEGER PRIMARY KEY` ovat omia
ratkaisuja. MariaDB:n `BOOLEAN` on `TINYINT(1)`, joten tuloste näyttää
ykkösen. Lisäys ja palautus on kaikissa sama:

```{.sql tiedosto="esimerkit/palvelimet/13-murre.pg" osa="lisays"}
```

Upsertin syntaksi eroaa. PostgreSQL ja SQLite käyttävät muotoa
`ON CONFLICT`, joka nimeää ristiriidan sarakkeet, MariaDB muotoa
`ON DUPLICATE KEY UPDATE`, joka reagoi mihin tahansa yksilölliseen
avaimeen:

```{.sql tiedosto="esimerkit/palvelimet/13-murre.maria" osa="upsert"}
```

Sivutukseen kaikki tuntevat `LIMIT`- ja `OFFSET`-muodon; standardin
`OFFSET ... FETCH FIRST` toimii PostgreSQL:ssä ja MariaDB 10.6:sta
lähtien, mutta ei SQLitessä:

```{.sql tiedosto="esimerkit/palvelimet/13-murre.pg" osa="sivutus"}
```

### Aikaleimat ja aikavyöhykkeet

Ajanhetki (tapahtuma, kirjautuminen, maksu) tallennetaan
aikavyöhykkeellisenä, seinäkelloaika (kokouksen alku paikallista
aikaa) ilman. Tyyppien nimet ja käytös eroavat:

```{.sql tiedosto="esimerkit/palvelimet/13-murre.pg" osa="aika"}
```

```{.sql tiedosto="esimerkit/palvelimet/13-murre.maria" osa="aika"}
```

PostgreSQL:n `timestamptz` tallentaa hetken UTC:nä ja näyttää sen
istunnon aikavyöhykkeessä; `timestamp` on pelkkä seinäkelloaika.
MariaDB:n `TIMESTAMP` muunnetaan samoin istunnon vyöhykkeen mukaan, mutta
sen arvoalue päättyy MariaDB 10.11:ssä vuoteen 2038, ja `DATETIME` tallennetaan
sellaisenaan. SQLitessä aika on tekstiä tai lukua, ja vyöhykkeestä
huolehtii sovellus.

### Eristystasot ja MVCC

```{.sql tiedosto="esimerkit/palvelimet/13-murre.pg" osa="eristys"}
```

```{.sql tiedosto="esimerkit/palvelimet/13-murre.maria" osa="eristys"}
```

PostgreSQL:n tuloste:

```{.tuloste tiedosto="esimerkit/palvelimet/13-murre.pg.odotettu"}
```

MariaDB:n tuloste:

```{.tuloste tiedosto="esimerkit/palvelimet/13-murre.maria.odotettu"}
```

Oletuseristystasot eroavat: PostgreSQL, Oracle ja SQL Server käyttävät
tasoa *read committed*, InnoDB tasoa *repeatable read* ja SQLite on aina
sarjallistuva. Sama sovelluskoodi voi siksi käyttäytyä eri tavoin
rinnakkaisessa kuormassa. InnoDB:n *repeatable read* lukitsee
päivityksissä myös indeksin välejä (*gap locks*), mikä estää haamurivejä
mutta aiheuttaa lukkiutumisia, joita PostgreSQL:ssä ei synny.
PostgreSQL:n *repeatable read* taas on tilannevedos, joka keskeyttää
ristiriitaisen päivityksen virheellä, ja sovelluksen on yritettävä
uudelleen (luku 10). SQL Serverissä lukijat odottavat oletuksena
kirjoittajia, ellei versioituja lukuja (*read committed snapshot*) ole
kytketty päälle.

## Vertailu

| Järjestelmä | Vahvuudet | Tyypillinen käyttö | Lisenssi |
|------------|------------------------------|------------------------------|----------------|
| SQLite | ei palvelinta, yksi tiedosto, luotettava | sovelluksen oma data, mobiili, testit | public domain |
| PostgreSQL | tyypit, JSONB, laajennukset, standardituki | uudet palvelinsovellukset, paikkatieto | PostgreSQL (vapaa) |
| MariaDB, MySQL | helppo ylläpito, replikointi, hosting-tuki | web-sovellukset, sisällönhallinta | GPL (MySQL myös kaupallinen) |
| Oracle | yritysominaisuudet, RAC, PL/SQL | pankit, ERP, suuret organisaatiot | kaupallinen |
| SQL Server | Microsoft-ympäristö, T-SQL, työkalut | .NET-sovellukset, raportointi | kaupallinen |
| DuckDB | sarakepohjainen, sulautettava analytiikka | data-analyysi, tiedostojen kyselyt | MIT |

## Käytännössä

- **Oletuksena PostgreSQL** uuteen palvelinsovellukseen, ellei
  ympäristö, olemassa oleva osaaminen tai ohjelmisto (esimerkiksi
  WordPress) määrää muuta. SQLite on hyvä valinta, kun kirjoittajia on
  yksi prosessi.
- **Testaa samalla järjestelmällä kuin tuotanto.** Tämän luvun erot
  (jakolasku, vertailu, NULLien järjestys, eristystaso) eivät näy, jos
  testit ajetaan SQLitellä ja tuotanto MariaDB:llä. Oikea tietokanta
  testeissä saadaan kontista; ks. taito *Integraatiotestaus ja
  Testcontainers*.
- **Kirjoita järjestys ja tyypit auki**: `ORDER BY` NULL-käsittelyineen,
  `CAST` jakolaskuun ja aikavyöhykkeellinen tyyppi ajanhetkille. Silloin
  tulos ei riipu järjestelmän oletuksista.
- **Lajittelujärjestys valitaan tietoisesti.** Kirjainkoosta riippumaton
  vertailu on käyttäjälle mukava haussa, mutta tunnisteille, tiivisteille
  ja salasanoille tarvitaan binäärinen vertailu.
- **Siirrettävyys maksaa.** Standardin osajoukkoon rajoittuminen jättää
  käyttämättä järjestelmän parhaat ominaisuudet. Yleensä on parempi
  valita järjestelmä ja käyttää sitä kunnolla, ja eristää murrekohtainen
  SQL tietovarastokerrokseen (luku 15).

## Itsearviointi

- Osaat kertoa SQLiten, PostgreSQL:n, MariaDB:n, Oraclen ja SQL Serverin
  vahvuudet, tyypilliset käyttökohteet ja lisenssimallit.
- Osaat tunnistaa murre-erot automaattisissa avaimissa, upsertissa,
  sivutuksessa, merkkijonojen vertailussa ja jakolaskussa.
- Osaat valita aikaleimalle oikean tyypin ja selittää, miten
  aikavyöhyke vaikuttaa tallennukseen ja näyttämiseen.
- Osaat selittää, miten oletuseristystasot ja MVCC:n toteutukset eroavat
  ja miksi se vaikuttaa sovelluksen käytökseen.
