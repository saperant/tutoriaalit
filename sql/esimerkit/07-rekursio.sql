-- Rekursiivinen CTE: kategoriapuu ja polut.
.headers on
.mode box

-- @alku taulu
CREATE TABLE kategoria (
    id       INTEGER PRIMARY KEY,
    nimi     TEXT NOT NULL,
    ylempi   INTEGER REFERENCES kategoria (id)
) STRICT;

INSERT INTO kategoria VALUES
    (1, 'Kaikki', NULL),
    (2, 'Keittiö', 1), (3, 'Kahvi ja tee', 2), (4, 'Laitteet', 3),
    (5, 'Astiat', 2), (6, 'Puutarha', 1);
-- @loppu taulu

-- @alku rekursio
WITH RECURSIVE polku (id, nimi, taso, reitti) AS (
    SELECT id, nimi, 0, nimi
    FROM kategoria WHERE ylempi IS NULL
    UNION ALL
    SELECT k.id, k.nimi, p.taso + 1, p.reitti || ' > ' || k.nimi
    FROM kategoria AS k
    JOIN polku AS p ON k.ylempi = p.id
)
SELECT taso, reitti FROM polku ORDER BY reitti;
-- @loppu rekursio
