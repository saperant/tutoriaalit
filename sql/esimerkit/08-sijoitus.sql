-- Sijoitusfunktiot.
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

-- @alku top-n
-- Kunkin kategorian kallein tuote: ROW_NUMBER ryhmän sisällä.
WITH jarjestetty AS (
    SELECT kategoria, nimi, hinta_snt,
           row_number() OVER (PARTITION BY kategoria
                              ORDER BY hinta_snt DESC) AS nro
    FROM tuote
)
SELECT kategoria, nimi, hinta_snt
FROM jarjestetty
WHERE nro = 1
ORDER BY kategoria;
-- @loppu top-n

-- @alku rank
SELECT a.nimi,
       count(t.id) AS tilauksia,
       rank()       OVER (ORDER BY count(t.id) DESC) AS rank,
       dense_rank() OVER (ORDER BY count(t.id) DESC) AS dense_rank
FROM asiakas AS a
LEFT JOIN tilaus AS t ON t.asiakas_id = a.id
GROUP BY a.id
ORDER BY tilauksia DESC, a.nimi;
-- @loppu rank
