# SQL ja relaatiotietokannat

Tiivis suomenkielinen johdatus tietomallinnukseen, kyselyihin,
transaktioihin ja indekseihin. Esimerkit ajetaan SQLite 3.45:llä, ja
erot PostgreSQL:ään kerrotaan. Valmiit dokumentit: [sql.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sql.pdf)
ja pikaopas [sql-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sql-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, standardit, SQLite ja PostgreSQL, työkalut
2. Relaatiomalli ja normalisointi – avaimet, anomaliat, 3NF,
   verkkokaupan skeema
3. Kyselyt – suoritusjärjestys, `CASE`, päivämäärät, puoliavoimet välit
4. NULL ja kolmiarvoinen logiikka – `NOT IN` -ansa, NULL koosteissa
5. Liitokset – ulkoliitos, semi- ja anti-liitos, rivien
   moninkertaistuminen
6. Koosteet ja ryhmittely – `HAVING`, `FILTER`, `string_agg`
7. Alikyselyt, CTE:t ja näkymät – rekursio, päiväsarjat
8. Ikkunafunktiot – top-N ryhmittäin, kumulatiiviset summat, `lag`
9. Rajoitteet ja eheys – viiteavaimet, `CHECK`, `STRICT`, triggerit
10. Muutokset ja transaktiot – UPSERT, `RETURNING`, eristystasot,
    SQLiten lukitus
11. Indeksit ja suorituskyky – `EXPLAIN QUERY PLAN`, yhdistelmä- ja
    osittaiset indeksit, avainsivutus
12. SQL sovelluksesta – parametrit ja injektio, transaktiot Pythonissa,
    N+1, migraatiot
13. Lopuksi – nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # ajaa SQL-esimerkit sqlite3:lla, Python-esimerkit
              # ruffilla, mypy --strictillä ja Pythonilla
make pdf      # rakentaa sql.pdf:n ja sql-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
Kehityskontti: `.devcontainer/sql`.
