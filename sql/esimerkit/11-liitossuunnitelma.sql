-- Kolmen taulun kyselyn suunnitelma: liitosjärjestys ja järjestäminen.
.headers on
.mode box
-- @alku data
CREATE TABLE asiakas (
    id       INTEGER PRIMARY KEY,
    nimi     TEXT NOT NULL,
    kaupunki TEXT NOT NULL
) STRICT;
CREATE TABLE tilaus (
    id         INTEGER PRIMARY KEY,
    asiakas_id INTEGER NOT NULL REFERENCES asiakas (id),
    paiva      TEXT NOT NULL
) STRICT;
CREATE TABLE tilausrivi (
    tilaus_id INTEGER NOT NULL REFERENCES tilaus (id),
    tuote_id  INTEGER NOT NULL,
    maara     INTEGER NOT NULL,
    PRIMARY KEY (tilaus_id, tuote_id)
) STRICT;
CREATE INDEX tilaus_asiakas ON tilaus (asiakas_id);

-- 2 000 asiakasta 20 kaupungissa, 100 000 tilausta, 300 000 riviä.
WITH RECURSIVE n (i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n
                         WHERE i < 100000)
INSERT INTO tilaus
SELECT i, i % 2000 + 1,
       date('2026-01-01', '+' || (i * 7 % 365) || ' days')
FROM n;
INSERT INTO asiakas
SELECT id, 'Asiakas ' || id, 'Kaupunki ' || (id % 20)
FROM tilaus WHERE id <= 2000;
INSERT INTO tilausrivi
SELECT t.id, k.tuote, 1 + (t.id + k.tuote) % 3
FROM tilaus AS t, (SELECT 1 AS tuote UNION ALL SELECT 2
                   UNION ALL SELECT 3) AS k;
ANALYZE;
-- @loppu data

-- @alku kysely
EXPLAIN QUERY PLAN
SELECT a.nimi, sum(r.maara) AS kappaleita
FROM asiakas AS a
JOIN tilaus AS t ON t.asiakas_id = a.id
JOIN tilausrivi AS r ON r.tilaus_id = t.id
WHERE a.kaupunki = 'Kaupunki 7'
GROUP BY a.id
ORDER BY kappaleita DESC
LIMIT 5;
-- @loppu kysely

SELECT a.nimi, sum(r.maara) AS kappaleita
FROM asiakas AS a
JOIN tilaus AS t ON t.asiakas_id = a.id
JOIN tilausrivi AS r ON r.tilaus_id = t.id
WHERE a.kaupunki = 'Kaupunki 7'
GROUP BY a.id
ORDER BY kappaleita DESC, a.id
LIMIT 3;
