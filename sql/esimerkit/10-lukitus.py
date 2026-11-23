"""Samanaikaisuus SQLitessä: yksi kirjoittaja, lukijat näkevät
tilannekuvan."""

import sqlite3


def avaa(polku: str) -> sqlite3.Connection:
    # timeout=0: ei odoteta lukkoa, jotta tilanne näkyy heti.
    # Tuotannossa odotusaika on tyypillisesti sekunteja.
    return sqlite3.connect(polku, timeout=0, autocommit=True)


def saldo(yhteys: sqlite3.Connection) -> int:
    (arvo,) = yhteys.execute(
        "SELECT saldo FROM varasto WHERE tuote_id = 1").fetchone()
    return int(arvo)


def main() -> None:
    a = avaa("kauppa.db")
    # @alku wal
    a.execute("PRAGMA journal_mode = WAL")
    # @loppu wal
    a.execute("CREATE TABLE varasto (tuote_id INTEGER PRIMARY KEY, "
              "saldo INTEGER NOT NULL) STRICT")
    a.execute("INSERT INTO varasto VALUES (1, 10)")
    b = avaa("kauppa.db")

    # @alku lukko
    a.execute("BEGIN IMMEDIATE")          # A varaa kirjoitusoikeuden
    a.execute("UPDATE varasto SET saldo = saldo - 3 WHERE tuote_id = 1")
    print("A näkee:", saldo(a))
    print("B näkee:", saldo(b))           # sitomaton muutos ei näy
    try:
        b.execute("BEGIN IMMEDIATE")      # toinen kirjoittaja
    except sqlite3.OperationalError as virhe:
        print("B ei saa kirjoittaa:", virhe)
    a.execute("COMMIT")
    print("B näkee sitomisen jälkeen:", saldo(b))
    # @loppu lukko
    a.close()
    b.close()


if __name__ == "__main__":
    main()
