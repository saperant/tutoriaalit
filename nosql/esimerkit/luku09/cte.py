"""Samat kyselyt PostgreSQLin rekursiivisella CTE:llä."""

from nosql.kontit import Ymparisto, aja
from nosql.verkosto import OSTI, SEURAA


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.postgres()
    kanta.execute("DROP TABLE IF EXISTS seuraa, osti")
    kanta.execute("CREATE TABLE seuraa (kuka text, kenta text)")
    kanta.execute("CREATE TABLE osti (kuka text, tuote text)")
    with kanta.cursor() as k:
        k.executemany("INSERT INTO seuraa VALUES (%s, %s)", SEURAA)
        k.executemany("INSERT INTO osti VALUES (%s, %s)", OSTI)

    # @alku suositus
    rivit = kanta.execute("""
        SELECT muu.tuote, count(DISTINCT muu.kuka) AS ostajia
        FROM osti t
        JOIN osti muu ON muu.kuka = t.kuka AND muu.tuote <> t.tuote
        WHERE t.tuote = 'keitin'
        GROUP BY muu.tuote
        ORDER BY ostajia DESC, muu.tuote""").fetchall()
    print("suositukset:", rivit)
    # @loppu suositus

    # @alku polku
    rivi = kanta.execute("""
        WITH RECURSIVE polut (loppu, polku) AS (
            SELECT kenta, ARRAY['aino', kenta]
            FROM seuraa WHERE kuka = 'aino'
          UNION ALL
            SELECT s.kenta, p.polku || s.kenta
            FROM polut p JOIN seuraa s ON s.kuka = p.loppu
            WHERE s.kenta <> ALL (p.polku)       -- ei kehiä
        )
        SELECT polku FROM polut WHERE loppu = 'pekka'
        ORDER BY cardinality(polku), polku LIMIT 1""").fetchone()
    print("lyhin polku:", " -> ".join(rivi[0] if rivi else []))
    # @loppu polku


if __name__ == "__main__":
    aja(ajo)
