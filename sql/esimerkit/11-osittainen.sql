-- Osittainen indeksi harvinaiselle arvolle.
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

-- @alku osittainen
-- Vain 2 % tilauksista on avoimia: indeksoidaan vain ne.
CREATE INDEX tilaus_avoin ON tilaus (paiva) WHERE tila = 'avoin';
ANALYZE;
EXPLAIN QUERY PLAN
SELECT id, paiva FROM tilaus WHERE tila = 'avoin' ORDER BY paiva;
SELECT count(*) AS avoimia FROM tilaus WHERE tila = 'avoin';
-- @loppu osittainen
