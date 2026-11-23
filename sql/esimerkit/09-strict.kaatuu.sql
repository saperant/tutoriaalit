-- Joustava tyypitys ja STRICT-taulut.
.headers on
.mode box

-- @alku joustava
CREATE TABLE hinta_vanha (tuote TEXT, hinta_snt INTEGER);
INSERT INTO hinta_vanha VALUES ('Kahvi', 899), ('Tee', '5,49');
SELECT tuote, hinta_snt, typeof(hinta_snt) AS tyyppi FROM hinta_vanha;
-- @loppu joustava

-- @alku tiukka
CREATE TABLE hinta (tuote TEXT NOT NULL, hinta_snt INTEGER NOT NULL)
STRICT;
INSERT INTO hinta VALUES ('Kahvi', 899);
INSERT INTO hinta VALUES ('Tee', '5,49');
-- @loppu tiukka
SELECT 'ei suoriteta';
