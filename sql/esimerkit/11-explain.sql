-- Kyselysuunnitelma ennen indeksiä ja sen jälkeen.
.headers on
.mode box
-- @alku data
CREATE TABLE tilaus (
    id         INTEGER PRIMARY KEY,
    asiakas_id INTEGER NOT NULL,
    paiva      TEXT NOT NULL,
    summa_snt  INTEGER NOT NULL,
    tila       TEXT NOT NULL
) STRICT;

-- 100 000 tilausta 2 000 asiakkaalle vuodelle 2026.
WITH RECURSIVE n (i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n
                         WHERE i < 100000)
INSERT INTO tilaus
SELECT i,
       i % 2000 + 1,
       date('2026-01-01', '+' || (i * 7 % 365) || ' days'),
       (i * 7919) % 20000 + 500,
       CASE WHEN i % 50 = 0 THEN 'avoin' ELSE 'toimitettu' END
FROM n;
ANALYZE;
-- @loppu data

-- @alku ennen
EXPLAIN QUERY PLAN
SELECT id, paiva, summa_snt FROM tilaus WHERE asiakas_id = 42;
-- @loppu ennen

-- @alku jalkeen
CREATE INDEX tilaus_asiakas ON tilaus (asiakas_id);
ANALYZE;
EXPLAIN QUERY PLAN
SELECT id, paiva, summa_snt FROM tilaus WHERE asiakas_id = 42;
-- @loppu jalkeen

-- @alku funktio
-- Sarakkeeseen kohdistuva funktio estää indeksin käytön ...
CREATE INDEX tilaus_paiva ON tilaus (paiva);
EXPLAIN QUERY PLAN
SELECT count(*) FROM tilaus WHERE strftime('%m', paiva) = '03';
-- ... mutta välin ehto käyttää sitä.
EXPLAIN QUERY PLAN
SELECT count(*) FROM tilaus
WHERE paiva >= '2026-03-01' AND paiva < '2026-04-01';
-- @loppu funktio
