-- Normalisoimaton taulu ja päivitysanomalia.
.headers on
.mode box

-- @alku taulu
CREATE TABLE tilaus_litea (
    tilaus_id      INTEGER,
    asiakas_nimi   TEXT,
    asiakas_sposti TEXT,
    tuotteet       TEXT          -- pilkuilla erotettu lista
);

INSERT INTO tilaus_litea VALUES
    (1, 'Aino Virtanen', 'aino@esimerkki.fi', 'Kahvi 500 g, Suodatinpaperi'),
    (2, 'Aino Virtanen', 'aino@esimerkki.fi', 'Termosmuki');
-- @loppu taulu

-- @alku anomalia
-- Aino vaihtaa osoitetta, mutta päivitys osuu vain yhteen riviin.
UPDATE tilaus_litea SET asiakas_sposti = 'aino.v@esimerkki.fi'
WHERE tilaus_id = 2;

SELECT DISTINCT asiakas_nimi, asiakas_sposti FROM tilaus_litea;

-- Monta arvoa yhdessä sarakkeessa: kuka tilasi kahvia?
SELECT tilaus_id FROM tilaus_litea WHERE tuotteet LIKE '%Kahvi%';
-- @loppu anomalia
