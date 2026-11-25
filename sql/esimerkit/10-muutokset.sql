-- Rivien lisäys, muutos ja poisto: INSERT, UPDATE ja DELETE.
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

-- @alku insert
-- Sarakkeet nimetään aina: lause ei riipu taulun sarakejärjestyksestä,
-- ja pois jätetty sarake saa oletusarvonsa (tässä id:n).
INSERT INTO asiakas (nimi, kaupunki) VALUES ('Ville Salo', 'Turku');

-- Monta riviä yhdellä lauseella.
INSERT INTO tuote (nimi, kategoria, hinta_snt) VALUES
    ('Kaakao 250 g', 'elintarvike', 449),
    ('Teesihti', 'tarvikkeet', 690);

-- Rivit toisen kyselyn tuloksesta.
CREATE TABLE kanta_asiakas (
    asiakas_id INTEGER PRIMARY KEY REFERENCES asiakas (id),
    tilauksia  INTEGER NOT NULL
) STRICT;
INSERT INTO kanta_asiakas (asiakas_id, tilauksia)
SELECT asiakas_id, count(*)
FROM tilaus
GROUP BY asiakas_id
HAVING count(*) >= 2;
-- @loppu insert

SELECT * FROM kanta_asiakas ORDER BY asiakas_id;

-- @alku update
-- Sama WHERE-ehto ensin SELECT-lauseessa: mihin riveihin muutos osuu?
SELECT id, nimi, hinta_snt FROM tuote WHERE kategoria = 'laitteet';

UPDATE tuote
SET hinta_snt = hinta_snt * 90 / 100
WHERE kategoria = 'laitteet';
SELECT changes() AS muuttui;
-- @loppu update

SELECT id, nimi, hinta_snt FROM tuote WHERE kategoria = 'laitteet';

-- @alku delete
-- Asiakkaat, joilla ei ole yhtään tilausta.
DELETE FROM asiakas
WHERE NOT EXISTS (
    SELECT 1 FROM tilaus AS t WHERE t.asiakas_id = asiakas.id);
SELECT changes() AS poistui;
-- @loppu delete

SELECT id, nimi FROM asiakas ORDER BY id;
