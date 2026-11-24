"""Cassandra: taulut kyselyjen mukaan, partitio- ja klusterointiavain."""

from cassandra import InvalidRequest

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    s = ymp.cassandra()
    s.execute("DROP KEYSPACE IF EXISTS kauppa07")
    # @alku avaruus
    s.execute("""CREATE KEYSPACE kauppa07 WITH replication =
                 {'class': 'SimpleStrategy', 'replication_factor': 1}""")
    s.set_keyspace("kauppa07")
    # @loppu avaruus

    # @alku taulu
    s.execute("""
        CREATE TABLE tilaukset_asiakkaittain (
            asiakas  text,
            paiva    date,
            tilaus   text,
            summa    decimal,
            PRIMARY KEY ((asiakas), paiva, tilaus)
        ) WITH CLUSTERING ORDER BY (paiva DESC, tilaus ASC)""")
    # @loppu taulu

    # @alku lisays
    lisays = s.prepare("""INSERT INTO tilaukset_asiakkaittain
                          (asiakas, paiva, tilaus, summa)
                          VALUES (?, ?, ?, ?)""")
    for rivi in [("aino", "2026-11-02", "T1", 107),
                 ("eero", "2026-11-03", "T2", 299),
                 ("aino", "2026-11-20", "T3", 168),
                 ("ilona", "2026-11-21", "T4", 90),
                 ("aino", "2026-11-21", "T5", 49)]:
        s.execute(lisays, rivi)
    # @loppu lisays

    # @alku haku
    uusimmat = s.execute("""SELECT paiva, tilaus, summa
                            FROM tilaukset_asiakkaittain
                            WHERE asiakas = 'aino' LIMIT 2""")
    for r in uusimmat:
        print("aino:", r.paiva, r.tilaus, r.summa)
    marraskuu = s.execute("""SELECT count(*) FROM tilaukset_asiakkaittain
                             WHERE asiakas = 'aino'
                             AND paiva >= '2026-11-15'""").one()
    print("aino, 15.11. jalkeen:", marraskuu[0])
    # @loppu haku

    # @alku kielletty
    try:
        s.execute("""SELECT * FROM tilaukset_asiakkaittain
                     WHERE summa > 100""")
    except InvalidRequest as virhe:
        print("haku ilman partitioavainta:", "ALLOW FILTERING" in str(virhe))
    # @loppu kielletty

    # @alku toinen
    s.execute("""
        CREATE TABLE tilaukset_paivittain (
            paiva    date,
            tilaus   text,
            asiakas  text,
            summa    decimal,
            PRIMARY KEY ((paiva), tilaus))""")
    paivittain = s.prepare("""INSERT INTO tilaukset_paivittain
                              (paiva, tilaus, asiakas, summa)
                              VALUES (?, ?, ?, ?)""")
    for r in s.execute("SELECT * FROM tilaukset_asiakkaittain"):
        s.execute(paivittain, (r.paiva, r.tilaus, r.asiakas, r.summa))
    paiva = s.execute("""SELECT tilaus, asiakas FROM tilaukset_paivittain
                         WHERE paiva = '2026-11-21'""")
    print("21.11.:", [(r.tilaus, r.asiakas) for r in paiva])
    # @loppu toinen


if __name__ == "__main__":
    aja(ajo)
