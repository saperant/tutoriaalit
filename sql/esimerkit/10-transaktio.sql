-- Transaktio ja tallennuspiste.
-- Verkkokaupan skeema ja data: ks. luku 2.
-- @alku asetukset
.headers on
.mode box
PRAGMA foreign_keys = ON;

CREATE TABLE asiakas (
    id       INTEGER PRIMARY KEY,
    nimi     TEXT NOT NULL,
    kaupunki TEXT
) STRICT;

CREATE TABLE tuote (
    id        INTEGER PRIMARY KEY,
    nimi      TEXT NOT NULL UNIQUE,
    kategoria TEXT NOT NULL,
    hinta_snt INTEGER NOT NULL CHECK (hinta_snt >= 0)
) STRICT;

CREATE TABLE tilaus (
    id         INTEGER PRIMARY KEY,
    asiakas_id INTEGER NOT NULL REFERENCES asiakas (id),
    paiva      TEXT NOT NULL CHECK (paiva = date(paiva))
) STRICT;

CREATE TABLE tilausrivi (
    tilaus_id INTEGER NOT NULL REFERENCES tilaus (id),
    tuote_id  INTEGER NOT NULL REFERENCES tuote (id),
    maara     INTEGER NOT NULL CHECK (maara > 0),
    PRIMARY KEY (tilaus_id, tuote_id)
) STRICT;

INSERT INTO asiakas (id, nimi, kaupunki) VALUES
    (1, 'Aino Virtanen', 'Helsinki'),
    (2, 'Matti Korhonen', 'Tampere'),
    (3, 'Liisa Nieminen', 'Oulu'),
    (4, 'Juha Mäkinen', 'Helsinki'),
    (5, 'Sari Laine', NULL);

INSERT INTO tuote (id, nimi, kategoria, hinta_snt) VALUES
    (1, 'Kahvi 500 g', 'elintarvike', 899),
    (2, 'Tee 100 g', 'elintarvike', 549),
    (3, 'Termosmuki', 'astiat', 2490),
    (4, 'Kahvimylly', 'laitteet', 5900),
    (5, 'Suodatinpaperi', 'tarvikkeet', 299),
    (6, 'Maitovaahdotin', 'laitteet', 3490);

INSERT INTO tilaus (id, asiakas_id, paiva) VALUES
    (1, 1, '2026-10-02'),
    (2, 1, '2026-10-15'),
    (3, 2, '2026-10-15'),
    (4, 3, '2026-10-20'),
    (5, 4, '2026-11-01'),
    (6, 2, '2026-11-03');

INSERT INTO tilausrivi (tilaus_id, tuote_id, maara) VALUES
    (1, 1, 2), (1, 5, 1),
    (2, 3, 1),
    (3, 1, 1), (3, 2, 3), (3, 4, 1),
    (4, 6, 1),
    (5, 1, 4), (5, 5, 2),
    (6, 3, 2);
-- @loppu asetukset

CREATE TABLE varasto (
    tuote_id INTEGER PRIMARY KEY REFERENCES tuote (id),
    saldo    INTEGER NOT NULL CHECK (saldo >= 0)
) STRICT;
INSERT INTO varasto SELECT id, 10 FROM tuote;

-- @alku transaktio
-- Tilaus ja varaston vähennys yhtenä kokonaisuutena.
BEGIN IMMEDIATE;
INSERT INTO tilaus (id, asiakas_id, paiva) VALUES (7, 3, '2026-11-20');
INSERT INTO tilausrivi VALUES (7, 4, 1), (7, 5, 3);
UPDATE varasto SET saldo = saldo - r.maara
FROM tilausrivi AS r
WHERE r.tilaus_id = 7 AND r.tuote_id = varasto.tuote_id;
COMMIT;
-- @loppu transaktio

-- @alku savepoint
-- Osittainen peruutus: kuponki hylätään, muu tilaus säilyy.
BEGIN;
INSERT INTO tilaus (id, asiakas_id, paiva) VALUES (8, 4, '2026-11-21');
INSERT INTO tilausrivi VALUES (8, 2, 2);
SAVEPOINT kuponki;
INSERT INTO tilausrivi VALUES (8, 3, 1);   -- kaupanpäällinen
ROLLBACK TO kuponki;                       -- ehto ei täyttynyt
RELEASE kuponki;
COMMIT;
-- @loppu savepoint

SELECT tilaus_id, tuote_id, maara FROM tilausrivi
WHERE tilaus_id >= 7 ORDER BY tilaus_id, tuote_id;
SELECT tuote_id, saldo FROM varasto WHERE saldo <> 10;
