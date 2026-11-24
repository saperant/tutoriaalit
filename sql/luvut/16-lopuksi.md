# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

Mallinnus ja eheys:

1. Normalisoi kolmanteen normaalimuotoon; denormalisoi vain mitattuun
   tarpeeseen ja automatisoi toiston ylläpito.
2. Jokaisella taululla on pääavain, ja luonnollinen avain on
   yksikäsitteinen.
3. `NOT NULL` on oletus. NULL vain, kun puuttuva arvo on mallissa
   mielekäs.
4. Säännöt rajoitteiksi: `CHECK`, `UNIQUE` ja viiteavaimet.
   SQLitessä `STRICT` ja `PRAGMA foreign_keys = ON`.
5. Rahat kokonaislukuina tai `numeric`-tyyppinä, ajat UTC:nä ISO 8601
   -muodossa tai aikatyypillä.

Kyselyt:

6. `ORDER BY` aina, kun järjestys merkitsee, ja yksikäsitteisellä
   avaimella, kun tulosta sivutetaan.
7. `NOT EXISTS` eikä `NOT IN` alikyselyn kanssa.
8. Älä koosta kahta rinnakkaista 1–N-liitosta samassa vaiheessa;
   kokoa ensin, liitä sitten.
9. CTE:t monivaiheisiin kyselyihin, ikkunafunktiot sijoituksiin,
   kumulatiivisiin summiin ja vertailuun edelliseen riviin.
10. Nimetyt sarakkeet sovelluksen kyselyissä, ei `SELECT *`.

Muutokset ja suorituskyky:

11. Atominen päivitys (`SET x = x - ?` ehdolla) luku–muokkaus–kirjoitus-
    kierroksen sijaan; UPSERT idempotenttiin lisäykseen.
12. Lyhyet transaktiot; joukkolisäykset yhdessä transaktiossa.
13. Indeksit kyselyjen perusteella; tarkista suunnitelma `EXPLAIN`-
    komennolla ja muista indeksien kirjoitushinta.
14. Ehto sarakkeeseen sellaisenaan, ei funktion sisään.
15. Avainsivutus suurille joukoille.

Sovellus:

16. Parametrit aina; tunnisteet sallittujen luettelosta.
17. Ei kyselyitä silmukassa (N+1).
18. Skeema migraatioilla versionhallinnassa.
19. SQL yhteen paikkaan tietovarastoon; ORM tavalliseen CRUDiin, SQL
    raportteihin ja joukkomuutoksiin.
20. Testit samalla tietokantajärjestelmällä kuin tuotanto.

Järjestelmät ja aikasarjat:

21. Tyypit, järjestys ja aikavyöhyke auki; älä luota järjestelmän
    oletuksiin (jakolasku, vertailu, NULLien paikka).
22. Ajanhetket aikavyöhykkeellisinä ja UTC:nä.
23. Aikasarja ensin relaatiokantaan: aika avaimessa, osiointi aikavälin
    mukaan, BRIN; säilytysaika osioita poistamalla.

## Lähteet ja jatkolukeminen

- **SQLiten dokumentaatio** (<https://sqlite.org/docs.html>) on tarkka
  ja kattava. Erityisesti sivut *Datatypes In SQLite*, *STRICT
  Tables*, *Query Planning*, *The SQLite Query Optimizer Overview* ja
  *Write-Ahead Logging* liittyvät tämän tutoriaalin aiheisiin. SQLiten
  lähdekoodi ja dokumentaatio ovat vapaata (*public domain*).
- **PostgreSQL:n dokumentaatio**
  (<https://www.postgresql.org/docs/current/>) sisältää myös hyvän
  SQL-oppaan. Luvut *Concurrency Control* ja *Indexes* kertovat
  eristystasoista ja indekseistä PostgreSQL:n näkökulmasta.
- **Use The Index, Luke** (<https://use-the-index-luke.com>), Markus
  Winandin kirja indekseistä ja kyselyjen suorituskyvystä eri
  tietokannoissa. Avainsivutus ja vasemman etuliitteen sääntö
  käsitellään siinä perusteellisesti.
- **Modern SQL** (<https://modern-sql.com>) kertoo standardin uusista
  ominaisuuksista ja niiden tuesta eri tietokannoissa.
- **Kirjat:** Bill Karwinin *SQL Antipatterns* käy läpi yleiset
  mallinnus- ja kyselyvirheet, kuten listat sarakkeissa ja EAV-mallin.
  Martin Kleppmannin *Designing Data-Intensive Applications* selittää
  transaktiot, eristystasot ja replikoinnin perusteellisesti.
- **OWASP SQL Injection Prevention Cheat Sheet**
  (<https://cheatsheetseries.owasp.org>) on injektion torjunnan
  tarkistuslista.

- **MariaDB Knowledge Base** (<https://mariadb.com/kb/>) ja **MySQL
  Reference Manual** (<https://dev.mysql.com/doc/>) kertovat
  murteiden ja InnoDB:n yksityiskohdat, kuten lukitukset ja
  lajittelujärjestykset.
- **TimescaleDB:n dokumentaatio** (<https://docs.timescale.com>)
  esittelee hypertaulut ja jatkuvat koosteet. Aikasarjojen pakkauksen
  perusartikkeli on Pelkonen ym., *Gorilla: A Fast, Scalable, In-Memory
  Time Series Database* (VLDB 2015).
- **SQLAlchemyn dokumentaatio** (<https://docs.sqlalchemy.org>) ja sen
  ORM-opas selittävät työyksikön, identiteettikartan ja latausstrategiat.
  **jOOQ** (<https://www.jooq.org>) ja Martin Fowlerin *Patterns of
  Enterprise Application Architecture* (2002), josta nimet *unit of
  work*, *identity map* ja *data mapper* ovat peräisin.

### Työkalut

- **sqlite3**-komentorivityökalu ja **DB Browser for SQLite**
  (<https://sqlitebrowser.org>) SQLitelle, **psql** ja **pgAdmin**
  PostgreSQL:lle, **DBeaver** (<https://dbeaver.io>) molemmille.
- **SQLFluff** (<https://sqlfluff.com>) tarkistaa ja muotoilee SQL:ää
  usealle murteelle.
- **DuckDB** (<https://duckdb.org>) on SQLiten tapaan sulautettava
  mutta analytiikkaan tehty sarakepohjainen tietokanta. Se lukee
  suoraan CSV- ja Parquet-tiedostoja samalla SQL:llä.

### Mihin tästä eteenpäin

Taitopuussa SQL on esitietona taidoille *Taustapalvelut*, jossa
tietokantaa käytetään HTTP-rajapinnan takana, ja *Skaalautuvien
järjestelmien suunnittelu*, jossa käsitellään replikointia, osittamista
ja välimuisteja. Datan analysointiin SQL:ää käytetään myös
tietovarastoissa ja DuckDB:n kaltaisissa työkaluissa.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
