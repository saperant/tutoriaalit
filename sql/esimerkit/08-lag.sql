-- LAG ja LEAD: muutokset edelliseen mittaukseen.
.headers on
.mode box
.nullvalue -

-- @alku data
CREATE TABLE lukema (
    mittari TEXT NOT NULL,
    aika    TEXT NOT NULL,
    kwh     INTEGER NOT NULL,
    PRIMARY KEY (mittari, aika)
) STRICT;

INSERT INTO lukema VALUES
    ('A', '2026-11-01', 1000), ('A', '2026-11-08', 1065),
    ('A', '2026-11-15', 1140), ('B', '2026-11-01', 500),
    ('B', '2026-11-15', 530);
-- @loppu data

-- @alku lag
SELECT mittari,
       aika,
       kwh,
       kwh - lag(kwh) OVER w                         AS kulutus,
       julianday(aika) - julianday(lag(aika) OVER w) AS pv
FROM lukema
WINDOW w AS (PARTITION BY mittari ORDER BY aika)
ORDER BY mittari, aika;
-- @loppu lag
