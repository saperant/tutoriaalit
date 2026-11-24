---
title: SQL ja relaatiotietokannat
subtitle: Pikaopas kokeneelle kehittäjälle · SQLite 3.45 · erot PostgreSQL:ään
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Avaa tai luo kanta | `sqlite3 kauppa.db`, muistissa `sqlite3 :memory:` |
| Aja tiedosto, pysähdy virheeseen | `sqlite3 -bail -batch -init x.sql :memory: .quit` |
| Tuloste | `.mode box`, `.headers on`, `.nullvalue NULL` |
| Skeema | `.tables`, `.schema tilaus`, `PRAGMA table_info(tilaus)` |
| Suunnitelma ja aika | `EXPLAIN QUERY PLAN ...`, `.eqp on`, `.timer on` |
| Tilastot | `ANALYZE` (SQLite), `ANALYZE` / `VACUUM ANALYZE` (PG) |
| PostgreSQL | `psql -d kanta`, `\d tilaus`, `EXPLAIN (ANALYZE, BUFFERS)` |

# Skeema

```{.sql tiedosto="esimerkit/pikaopas.sql" osa="skeema"}
```

- `STRICT` ja `PRAGMA foreign_keys = ON` aina SQLitessä.
- Rahat kokonaislukuina senteissä tai `numeric`; ajat UTC, ISO 8601.
- Viiteavainsarakkeelle indeksi itse (ei synny automaattisesti).
- Normalisoi 3NF:ään: sarake riippuu avaimesta, koko avaimesta eikä
  mistään muusta. Ei listoja sarakkeissa, ei EAV-mallia.

| Toimenpide | Kun |
|------------|-----|
| `ON DELETE RESTRICT` (oletus) | itsenäinen olio: asiakas, tuote |
| `ON DELETE CASCADE` | osa kokonaisuutta: tilausrivi |
| `ON DELETE SET NULL` | valinnainen yhteys |

# Kyselyt

Looginen järjestys: `FROM`/`JOIN` → `WHERE` → `GROUP BY` → `HAVING` →
`SELECT` (ikkunat) → `DISTINCT` → `ORDER BY` → `LIMIT`.

```{.sql tiedosto="esimerkit/pikaopas.sql" osa="kysely"}
```

| Tarve | Rakenne |
|-------|---------|
| onko paria | `EXISTS (SELECT 1 ...)` (semi-liitos) |
| ei paria | `NOT EXISTS` (anti-liitos), **ei** `NOT IN` |
| myös parittomat | `LEFT JOIN`, ehto oikeaan tauluun `ON`-osaan |
| ehdollinen kooste | `count(*) FILTER (WHERE ...)` |
| merkkijonolista | `string_agg(x, ', ' ORDER BY x)` |
| vaiheittain | `WITH a AS (...), b AS (...) SELECT ...` |
| hierarkia, sarja | `WITH RECURSIVE` + päättymisehto |

# NULL

- `x = NULL` on aina tuntematon: `IS NULL`, `IS NOT NULL`.
- NULL-turvallinen vertailu: `IS` / `IS NOT` (SQLite),
  `IS [NOT] DISTINCT FROM` (standardi, PG, SQLite 3.39+).
- `WHERE` hylkää tuntemattoman; `CHECK` hyväksyy sen.
- `count(*)` rivit, `count(x)` arvot; tyhjän joukon `sum` on NULL →
  `coalesce(sum(x), 0)`.
- Järjestys: SQLite NULL pienin, PG suurin → `NULLS LAST`.

# Ikkunafunktiot

```{.sql tiedosto="esimerkit/pikaopas.sql" osa="ikkuna"}
```

- Top-N ryhmittäin: `row_number()` CTE:ssä + `WHERE nro <= N`.
- `rank` jättää aukon tasatuloksen jälkeen, `dense_rank` ei.
- Oletuskehys on `RANGE ... CURRENT ROW` (vertaisrivit yhdessä);
  kirjoita `ROWS` auki, kun järjestys ei ole yksikäsitteinen.
- `lag(x)`, `lead(x)`, `sum(x) OVER ()` (osuus kokonaisuudesta).

# Muutokset ja transaktiot

```{.sql tiedosto="esimerkit/pikaopas.sql" osa="muutokset"}
```

- Atominen ehdollinen päivitys luku–muokkaus–kirjoitus-kierroksen
  sijaan: oikein kaikilla eristystasoilla.
- SQLite: yksi kirjoittaja, aina *serializable*; WAL-tila
  (`PRAGMA journal_mode = WAL`) ja `PRAGMA busy_timeout = 5000`.
  `BEGIN IMMEDIATE` kirjoittaville transaktioille.
- PostgreSQL: oletus *read committed* → *lost update*, jos sovellus
  lukee ja kirjoittaa. Korjaus: atominen `UPDATE`,
  `SELECT ... FOR UPDATE` tai `SERIALIZABLE` + uudelleenyritys.
- Joukkolisäys yhdessä transaktiossa: jokainen sitoutus on *fsync*.

# Indeksit

```{.sql tiedosto="esimerkit/pikaopas.sql" osa="indeksi"}
```

Tulos: `SEARCH ... USING COVERING INDEX ... (asiakas_id=? AND paiva>?)`,
eli yksi haku indeksistä eikä taulua lueta lainkaan.

| Suunnitelma | Merkitys |
|-------------|----------|
| `SCAN t` | koko taulu läpi |
| `SEARCH t USING INDEX i (x=?)` | haku indeksistä + rivin luku |
| `USING COVERING INDEX` | kaikki sarakkeet indeksistä |
| `USE TEMP B-TREE FOR ORDER BY` | erillinen järjestäminen |
| `AUTOMATIC ... INDEX` | indeksi puuttuu, rakennetaan kyselyn ajaksi |

- Yhdistelmäindeksi: yhtäsuuruussarakkeet ensin, väli tai järjestys
  viimeisenä; vasemman etuliitteen sääntö.
- Ei funktioita sarakkeen ympärille: ei `strftime('%m', paiva) = '03'`
  vaan `paiva >= '2026-03-01' AND paiva < '2026-04-01'`.
- Osittainen indeksi: `CREATE INDEX ... WHERE tila = 'avoin'`.
- Jokainen indeksi hidastaa kirjoituksia ja vie tilaa.

Avainsivutus (vakiohintainen sivu, ei toistoja eikä aukkoja):

```{.sql tiedosto="esimerkit/pikaopas.sql" osa="sivutus"}
```

# Sovelluksesta (Python)

| Tarve | Koodi |
|-------|-------|
| Yhteys | `sqlite3.connect(polku, autocommit=False)` (3.12+) |
| Parametrit | `execute("... WHERE id = ?", (id,))`, `:nimi` + dict |
| IN-lista | `", ".join("?" * len(arvot))` paikkamerkeiksi |
| Tunnisteet | sallittujen luettelosta, ei syötteestä |
| Transaktio | `with yhteys:` sitoo tai peruu (ei sulje) |
| Joukkolisäys | `executemany(sql, rivit)` |
| Kyselyjen laskenta | `yhteys.set_trace_callback(lista.append)` |
| Skeeman versio | `PRAGMA user_version`; Alembic, Flyway |

- **Ei koskaan** f-merkkijonoja tai `+`-yhdistämistä arvoille.
- N+1: kysely silmukassa → yksi liitos tai ennakkolataus
  (`selectinload`, `prefetch_related`).
- Testaa samalla tietokannalla kuin tuotannossa.

# Murre-erot

| Asia | SQLite | PostgreSQL | MariaDB |
|------|--------|------------|---------|
| Avain | `INTEGER PRIMARY KEY` | `GENERATED ALWAYS AS IDENTITY` | `AUTO_INCREMENT` |
| Totuusarvo | 0 / 1 | `boolean` | `BOOLEAN` = `TINYINT(1)` |
| Ajanhetki | ISO-teksti | `timestamptz` | `TIMESTAMP` (vyöhyke istunnosta) |
| Upsert | `ON CONFLICT` | `ON CONFLICT` | `ON DUPLICATE KEY UPDATE` |
| `RETURNING` | kyllä | kyllä | `INSERT`, `DELETE` |
| Sivutus | `LIMIT`/`OFFSET` | myös `FETCH FIRST` | myös `FETCH FIRST` |
| `7 / 2` | 3 | 3 | 3.5000 |
| `'a' = 'A'` | epätosi | epätosi | tosi (`_ci`-vertailu) |
| Merkkijonojen yhdistys | kaksi pystyviivaa | kaksi pystyviivaa | `CONCAT`; pystyviivat ovat TAI |
| NULL nousevassa | ensin | viimeisenä | ensin |
| Sarja | rekursiivinen CTE | `generate_series` | `seq_1_to_n` |
| Eristystaso | sarjallistuva | read committed | repeatable read |
| Viiteavaimet | `PRAGMA foreign_keys = ON` | aina | aina (InnoDB) |
| Samanaikaisuus | yksi kirjoittaja | MVCC, rivilukot | MVCC, rivi- ja välilukot |

# Aikasarjat ja rajapinnat

- Väli: `date_bin('15 min', aika, alku)`; aukot: `generate_series` +
  `LEFT JOIN`; viimeisin: `DISTINCT ON (anturi) ... ORDER BY aika DESC`.
- Iso aikasarja: osiointi aikavälin mukaan, BRIN-indeksi, säilytysaika
  `DETACH PARTITION` + `DROP`; TimescaleDB automatisoi.
- Tasot: ajuri (DB-API, JDBC) → tietovarasto (DAO) →
  kyselynrakentaja (SQLAlchemy Core, jOOQ) → ORM (SQLAlchemy, JPA).
- ORM: työyksikkö, identiteettikartta, laiska lataus → N+1;
  korjaus `selectinload`. Lokita tuotettu SQL kehityksessä.
