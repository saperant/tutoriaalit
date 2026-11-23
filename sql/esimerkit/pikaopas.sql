-- Pikaoppaan esimerkit: tiivis verkkokauppa.
.headers on
.mode box
.nullvalue NULL

-- @alku skeema
PRAGMA foreign_keys = ON;            -- SQLite: jokaiselle yhteydelle

CREATE TABLE asiakas (
    id       INTEGER PRIMARY KEY,    -- PG: bigint GENERATED ... IDENTITY
    email    TEXT NOT NULL UNIQUE,
    kaupunki TEXT                    -- NULL = ei tiedossa
) STRICT;

CREATE TABLE tilaus (
    id         INTEGER PRIMARY KEY,
    asiakas_id INTEGER NOT NULL REFERENCES asiakas (id),
    paiva      TEXT NOT NULL CHECK (paiva = date(paiva)),
    summa_snt  INTEGER NOT NULL CHECK (summa_snt >= 0)
) STRICT;
CREATE INDEX tilaus_asiakas_paiva ON tilaus (asiakas_id, paiva);
-- @loppu skeema

INSERT INTO asiakas VALUES (1, 'aino@x.fi', 'Helsinki'),
    (2, 'matti@x.fi', 'Tampere'), (3, 'sari@x.fi', NULL);
INSERT INTO tilaus VALUES (1, 1, '2026-10-02', 2097),
    (2, 1, '2026-10-15', 2490), (3, 2, '2026-10-15', 8446),
    (4, 2, '2026-11-03', 4980);

-- @alku kysely
SELECT a.email,
       count(t.id)                       AS tilauksia,
       coalesce(sum(t.summa_snt), 0)     AS yhteensa_snt
FROM asiakas AS a
LEFT JOIN tilaus AS t ON t.asiakas_id = a.id
WHERE a.kaupunki IS NOT 'Oulu'      -- NULL-turvallinen vertailu
GROUP BY a.id
HAVING count(t.id) < 5
ORDER BY yhteensa_snt DESC, a.id;
-- @loppu kysely

-- @alku ikkuna
WITH jarjestetty AS (
    SELECT asiakas_id, paiva, summa_snt,
           row_number() OVER w                    AS nro,
           sum(summa_snt) OVER (w ROWS UNBOUNDED PRECEDING) AS kertyma,
           summa_snt - lag(summa_snt) OVER w      AS muutos
    FROM tilaus
    WINDOW w AS (PARTITION BY asiakas_id ORDER BY paiva, id)
)
SELECT asiakas_id, paiva, kertyma, muutos
FROM jarjestetty WHERE nro <= 2;
-- @loppu ikkuna

-- @alku muutokset
INSERT INTO asiakas (email, kaupunki) VALUES ('aino@x.fi', 'Espoo')
ON CONFLICT (email) DO UPDATE SET kaupunki = excluded.kaupunki
RETURNING id, kaupunki;

BEGIN IMMEDIATE;                     -- kirjoittava transaktio
UPDATE tilaus SET summa_snt = summa_snt - 500
WHERE id = 3 AND summa_snt >= 500    -- tarkistus ja muutos yhdessä
RETURNING id, summa_snt;
COMMIT;
-- @loppu muutokset

-- @alku indeksi
EXPLAIN QUERY PLAN
SELECT id, paiva FROM tilaus
WHERE asiakas_id = 2 AND paiva >= '2026-11-01';
-- @loppu indeksi

-- @alku sivutus
SELECT id, paiva FROM tilaus
WHERE (paiva, id) > ('2026-10-15', 2)   -- edellisen sivun viimeinen
ORDER BY paiva, id
LIMIT 2;
-- @loppu sivutus
