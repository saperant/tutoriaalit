-- Sama kysely SQLitessä, PostgreSQL:ssä ja MariaDB:ssä.
-- @alku sama
SELECT 7 / 2 AS jako,
       'abc' = 'ABC' AS isot_pienet,
       'a' = 'a ' AS loppuvali,
       'a' || 'b' AS yhdistys;

SELECT x FROM (SELECT 2 AS x UNION ALL SELECT NULL
               UNION ALL SELECT 1) AS t
ORDER BY x;
-- @loppu sama
