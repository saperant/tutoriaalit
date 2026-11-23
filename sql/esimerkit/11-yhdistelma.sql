-- Yhdistelmäindeksi ja kattava indeksi.
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

-- @alku yhdistelma
CREATE INDEX asiakas_pv ON tilaus (asiakas_id, paiva);
ANALYZE;

-- Vasen etuliite: yhtäsuuruus ensin, sitten väli.
EXPLAIN QUERY PLAN
SELECT paiva FROM tilaus
WHERE asiakas_id = 42 AND paiva >= '2026-06-01';

-- Pelkkä paiva ei ole indeksin etuliite.
EXPLAIN QUERY PLAN
SELECT count(*) FROM tilaus WHERE paiva = '2026-06-01';
-- @loppu yhdistelma

-- @alku kattava
-- SELECT * hakee jokaiselle osumalle rivin taulusta ...
EXPLAIN QUERY PLAN
SELECT * FROM tilaus WHERE asiakas_id = 42 ORDER BY paiva;
-- ... tarvittavat sarakkeet löytyvät indeksistä suoraan.
EXPLAIN QUERY PLAN
SELECT paiva FROM tilaus WHERE asiakas_id = 42 ORDER BY paiva;
-- @loppu kattava
