-- Ensimmäinen tietokanta: taulu, rivit ja kysely.
.headers on
.mode box

CREATE TABLE mittaus (
    anturi   TEXT NOT NULL,
    aika     TEXT NOT NULL,          -- ISO 8601 -aikaleima
    lampotila REAL NOT NULL
) STRICT;

INSERT INTO mittaus (anturi, aika, lampotila) VALUES
    ('olohuone', '2026-11-20 08:00', 21.5),
    ('olohuone', '2026-11-20 12:00', 22.1),
    ('parveke',  '2026-11-20 08:00', -3.0),
    ('parveke',  '2026-11-20 12:00', -1.5);

SELECT anturi,
       count(*)       AS mittauksia,
       min(lampotila) AS alin,
       max(lampotila) AS ylin
FROM mittaus
GROUP BY anturi
ORDER BY anturi;
