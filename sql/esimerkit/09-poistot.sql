-- ON DELETE CASCADE ja RESTRICT.
.headers on
.mode box
PRAGMA foreign_keys = ON;

-- @alku skeema
CREATE TABLE asiakas (id INTEGER PRIMARY KEY, nimi TEXT NOT NULL) STRICT;
CREATE TABLE tilaus (
    id         INTEGER PRIMARY KEY,
    asiakas_id INTEGER NOT NULL
               REFERENCES asiakas (id) ON DELETE RESTRICT
) STRICT;
CREATE TABLE tilausrivi (
    tilaus_id INTEGER NOT NULL
              REFERENCES tilaus (id) ON DELETE CASCADE,
    tuote     TEXT NOT NULL,
    PRIMARY KEY (tilaus_id, tuote)
) STRICT;
-- @loppu skeema

INSERT INTO asiakas VALUES (1, 'Aino'), (2, 'Matti');
INSERT INTO tilaus VALUES (10, 1), (11, 2);
INSERT INTO tilausrivi VALUES (10, 'Kahvi'), (10, 'Tee'), (11, 'Muki');

-- @alku poisto
DELETE FROM tilaus WHERE id = 10;         -- rivit lähtevät mukana
SELECT tilaus_id, tuote FROM tilausrivi;

-- RESTRICT kaataisi poiston, koska asiakkaalla 2 on tilaus. Ehto
-- samassa lauseessa tekee poistosta turvallisen: 0 riviä, ei virhettä.
DELETE FROM asiakas WHERE id = 2
    AND NOT EXISTS (SELECT 1 FROM tilaus WHERE asiakas_id = 2);
SELECT changes() AS poistettu;
-- @loppu poisto
