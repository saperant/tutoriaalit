-- Ryhmittely, HAVING ja FILTER.
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

-- @alku ryhmittely
SELECT tu.kategoria,
       count(DISTINCT r.tilaus_id)          AS tilauksia,
       sum(r.maara)                         AS kappaleita,
       sum(r.maara * tu.hinta_snt)          AS myynti_snt
FROM tilausrivi AS r
JOIN tuote AS tu ON tu.id = r.tuote_id
GROUP BY tu.kategoria
HAVING myynti_snt > 5000
ORDER BY myynti_snt DESC;
-- @loppu ryhmittely

-- @alku filter
-- Ehdolliset koosteet yhdellä läpikäynnillä.
SELECT strftime('%Y-%m', t.paiva) AS kuukausi,
       count(*) AS tilauksia,
       count(*) FILTER (WHERE a.kaupunki = 'Helsinki') AS helsingista
FROM tilaus AS t
JOIN asiakas AS a ON a.id = t.asiakas_id
GROUP BY kuukausi
ORDER BY kuukausi;
-- @loppu filter
