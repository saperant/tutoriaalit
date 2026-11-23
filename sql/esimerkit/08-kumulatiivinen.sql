-- Kumulatiivinen summa ja liukuva keskiarvo.
.headers on
.mode box

-- @alku data
CREATE TABLE myynti (
    paiva     TEXT PRIMARY KEY,
    summa_eur INTEGER NOT NULL
) STRICT;

INSERT INTO myynti VALUES
    ('2026-11-01', 120), ('2026-11-02', 80), ('2026-11-03', 200),
    ('2026-11-04', 40),  ('2026-11-05', 160);
-- @loppu data

-- @alku ikkuna
SELECT paiva,
       summa_eur,
       sum(summa_eur) OVER (ORDER BY paiva) AS kumulatiivinen,
       round(avg(summa_eur) OVER (
           ORDER BY paiva ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 1) AS liukuva_ka_3pv,
       round(100.0 * summa_eur / sum(summa_eur) OVER (), 1)
           AS osuus_pros
FROM myynti
ORDER BY paiva;
-- @loppu ikkuna
