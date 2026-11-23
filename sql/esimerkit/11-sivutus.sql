-- OFFSET-sivutus ja avainsivutus.
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

CREATE INDEX tilaus_paiva_id ON tilaus (paiva, id);
ANALYZE;

-- @alku offset
-- Sivu 500: tietokanta käy läpi ja hylkää 9 980 riviä.
SELECT id, paiva FROM tilaus
ORDER BY paiva, id
LIMIT 3 OFFSET 9980;
-- @loppu offset

-- @alku avain
-- Sama sivu avaimella: jatketaan edellisen sivun viimeisestä rivistä.
SELECT id, paiva FROM tilaus
WHERE (paiva, id) > ('2026-02-06', 42658)
ORDER BY paiva, id
LIMIT 3;
-- @loppu avain

-- @alku suunnitelma
EXPLAIN QUERY PLAN
SELECT id, paiva FROM tilaus
WHERE (paiva, id) > ('2026-02-06', 42658)
ORDER BY paiva, id
LIMIT 3;
-- @loppu suunnitelma
