"""Elinaika, poistot ja kevyet transaktiot (LWT)."""

import time

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    s = ymp.cassandra()
    s.execute("DROP KEYSPACE IF EXISTS kauppa07p")
    s.execute("""CREATE KEYSPACE kauppa07p WITH replication =
                 {'class': 'SimpleStrategy', 'replication_factor': 1}""")
    s.set_keyspace("kauppa07p")
    s.execute("""CREATE TABLE kupongit (koodi text PRIMARY KEY,
                                        ale int, omistaja text)""")

    # @alku ttl
    s.execute("INSERT INTO kupongit (koodi, ale) VALUES ('KESA', 20) "
              "USING TTL 2")
    print("heti:", s.execute("SELECT ale FROM kupongit "
                             "WHERE koodi = 'KESA'").one().ale)
    time.sleep(3)
    print("3 s kuluttua:", s.execute("SELECT ale FROM kupongit "
                                     "WHERE koodi = 'KESA'").one())
    # @loppu ttl

    # @alku lwt
    s.execute("INSERT INTO kupongit (koodi, ale) VALUES ('JOULU', 15)")
    for kayttaja in ["aino", "eero"]:
        tulos = s.execute("UPDATE kupongit SET omistaja = %s "
                          "WHERE koodi = 'JOULU' IF omistaja = null",
                          (kayttaja,)).one()
        print(kayttaja, "lunasti:", tulos.applied)
    # @loppu lwt


if __name__ == "__main__":
    aja(ajo)
