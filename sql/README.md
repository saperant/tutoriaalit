# SQL ja relaatiotietokannat

Tiivis suomenkielinen johdatus tietomallinnukseen, kyselyihin,
transaktioihin ja indekseihin sekä tietokantajärjestelmien eroihin,
aikasarjoihin ja tietokannan käyttöön sovelluksesta. Perusesimerkit
ajetaan SQLite 3.45:llä; murre-erot, aikasarjat, ajurin tyyppimuunnokset
ja ORM ajetaan myös oikeilla PostgreSQL 16- ja MariaDB 10.11
-palvelimilla. Valmiit dokumentit: [sql.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sql.pdf)
ja pikaopas [sql-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sql-pikaopas.pdf).

## Sisältö

Luvut 2–11 ovat tietokannasta riippumatonta SQL:ää, luvut 12–13
käsittelevät järjestelmien eroja ja aikasarjoja ja luvut 14–15
tietokannan käyttöä sovelluksesta.

1. Johdanto – historia, standardit, SQLite ja PostgreSQL, työkalut,
   tutoriaalin rakenne
2. Relaatiomalli ja normalisointi – avaimet, anomaliat, 3NF,
   verkkokaupan skeema ja ER-kaavio
3. Kyselyt – suoritusjärjestys, `CASE`, päivämäärät, puoliavoimet välit
4. NULL ja kolmiarvoinen logiikka – `NOT IN` -ansa, NULL koosteissa
5. Liitokset – ulkoliitos, semi- ja anti-liitos, rivien
   moninkertaistuminen
6. Koosteet ja ryhmittely – `HAVING`, `FILTER`, `string_agg`
7. Alikyselyt, CTE:t ja näkymät – joukko-operaatiot (`UNION`,
   `INTERSECT`, `EXCEPT`), rekursio, päiväsarjat
8. Ikkunafunktiot – top-N ryhmittäin, kumulatiiviset summat, `lag`
9. Rajoitteet ja eheys – viiteavaimet, `CHECK`, `STRICT`, triggerit
10. Muutokset ja transaktiot – `INSERT`, `UPDATE`, `DELETE`, UPSERT,
    `RETURNING`, samanaikaisuuden poikkeamat ja eristystasot, SQLiten
    lukitus
11. Indeksit ja suorituskyky – B-puu, `EXPLAIN QUERY PLAN`,
    yhdistelmä- ja osittaiset indeksit, liitoksen suunnitelma,
    avainsivutus
12. Tietokantajärjestelmät – SQLite, PostgreSQL, MariaDB, Oracle ja
    SQL Server; sama kysely kolmessa järjestelmässä, aikavyöhykkeet,
    eristystasot
13. Aikasarjat – koosteet aikaväleittäin, aukot, osiointi ja BRIN,
    TimescaleDB, InfluxDB ja Prometheus, delta-of-delta-pakkaus
14. SQL sovelluksesta – yhteys, kursori ja tulosten tyypit, parametrit
    (ja SQL-injektio niiden puuttumisen seurauksena), transaktiot,
    virheiden käsittely ja uudelleenyritys, N+1, skeeman versiointi
15. Tietokanta sovelluksen rajapintana – ajuri, tietovarasto,
    kyselynrakentaja (SQLAlchemy Core, jOOQ), ORM ja tietokantakoodin
    testaus
16. Lopuksi – nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # ajaa SQL-esimerkit sqlite3:lla, Python-esimerkit
              # ruffilla, mypy --strictillä ja Pythonilla sekä
              # palvelinesimerkit väliaikaisilla PostgreSQL- ja
              # MariaDB-palvelimilla (esimerkit/palvelimet/aja.sh);
              # tarkistaa myös, että tulosteesta tuotettu kaavio
              # (kaaviot/tee.py) on ajan tasalla
make pdf      # rakentaa sql.pdf:n ja sql-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
Kehityskontti: `.devcontainer/sql`.
