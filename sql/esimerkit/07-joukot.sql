-- Joukko-operaatiot: UNION, INTERSECT ja EXCEPT.
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

-- @alku union
-- Hakukentän ehdotukset: asiakkaiden kaupungit ja tuotekategoriat
-- samassa luettelossa. Sarakkeita on oltava yhtä monta.
SELECT 'kaupunki' AS laji, kaupunki AS nimi
FROM asiakas
WHERE kaupunki IS NOT NULL
UNION
SELECT 'kategoria', kategoria
FROM tuote
ORDER BY laji, nimi;
-- @loppu union

-- @alku intersect
-- Asiakkaat, jotka tilasivat sekä lokakuussa että marraskuussa.
SELECT asiakas_id FROM tilaus
WHERE paiva >= '2026-10-01' AND paiva < '2026-11-01'
INTERSECT
SELECT asiakas_id FROM tilaus
WHERE paiva >= '2026-11-01' AND paiva < '2026-12-01'
ORDER BY asiakas_id;
-- @loppu intersect

-- @alku except
-- Asiakkaat, jotka tilasivat lokakuussa mutta eivät marraskuussa.
SELECT asiakas_id FROM tilaus
WHERE paiva >= '2026-10-01' AND paiva < '2026-11-01'
EXCEPT
SELECT asiakas_id FROM tilaus
WHERE paiva >= '2026-11-01' AND paiva < '2026-12-01'
ORDER BY asiakas_id;
-- @loppu except

-- @alku all
-- UNION poistaa toistot (myös NULL lasketaan yhdeksi arvoksi),
-- UNION ALL säilyttää kaikki rivit.
SELECT count(*) AS union_riveja FROM (
    SELECT kaupunki FROM asiakas UNION SELECT kaupunki FROM asiakas);
SELECT count(*) AS union_all_riveja FROM (
    SELECT kaupunki FROM asiakas UNION ALL SELECT kaupunki FROM asiakas);
-- @loppu all
