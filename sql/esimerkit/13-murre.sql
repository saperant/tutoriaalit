-- Sama tehtävä SQLitellä: automaattinen avain, RETURNING, upsert ja
-- sivutus. Vertaa tiedostoihin palvelimet/13-murre.pg ja .maria.
.headers on
.mode box
-- @alku taulu
CREATE TABLE tuote (
    id      INTEGER PRIMARY KEY,         -- rowid-alias, kasvaa itse
    koodi   TEXT NOT NULL UNIQUE,
    hinta   INTEGER NOT NULL,            -- senteissä
    aktiivinen INTEGER NOT NULL DEFAULT 1 -- ei omaa boolean-tyyppiä
) STRICT;
-- @loppu taulu
-- @alku lisays
INSERT INTO tuote (koodi, hinta) VALUES ('kahvi', 590), ('tee', 450)
RETURNING id, koodi;
-- @loppu lisays
-- @alku upsert
INSERT INTO tuote (koodi, hinta) VALUES ('tee', 480)
ON CONFLICT (koodi) DO UPDATE SET hinta = excluded.hinta;
-- @loppu upsert
-- @alku sivutus
SELECT koodi, hinta, aktiivinen FROM tuote
ORDER BY koodi
LIMIT 1 OFFSET 1;
-- @loppu sivutus
