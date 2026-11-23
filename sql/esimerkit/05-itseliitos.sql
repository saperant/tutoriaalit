-- Itseliitos: työntekijät ja heidän esihenkilönsä.
.headers on
.mode box
.nullvalue -

-- @alku taulu
CREATE TABLE tyontekija (
    id          INTEGER PRIMARY KEY,
    nimi        TEXT NOT NULL,
    esihenkilo  INTEGER REFERENCES tyontekija (id)
) STRICT;

INSERT INTO tyontekija VALUES
    (1, 'Kaisa', NULL), (2, 'Olli', 1), (3, 'Pirjo', 1), (4, 'Timo', 2);
-- @loppu taulu

-- @alku kysely
SELECT t.nimi AS tyontekija, e.nimi AS esihenkilo
FROM tyontekija AS t
LEFT JOIN tyontekija AS e ON e.id = t.esihenkilo
ORDER BY t.id;
-- @loppu kysely
