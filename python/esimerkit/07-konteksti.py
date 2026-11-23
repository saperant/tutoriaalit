"""Kontekstinhallinta: resurssi vapautuu myös virhetilanteessa."""

import contextlib
import sqlite3
from collections.abc import Iterator


# @alku transaktio
@contextlib.contextmanager
def transaktio(yhteys: sqlite3.Connection) -> Iterator[sqlite3.Cursor]:
    """Vahvistaa muutokset onnistuessa ja peruu ne poikkeuksessa."""
    kursori = yhteys.cursor()
    try:
        yield kursori
    except Exception:
        yhteys.rollback()
        print("  peruttu")
        raise
    else:
        yhteys.commit()
        print("  vahvistettu")
    finally:
        kursori.close()
# @loppu transaktio


# @alku kaytto
with contextlib.closing(sqlite3.connect(":memory:")) as yhteys:
    yhteys.execute("CREATE TABLE tili (nimi TEXT, saldo INTEGER)")
    yhteys.execute("INSERT INTO tili VALUES ('Ada', 100), ('Bob', 0)")
    yhteys.commit()

    print("siirto 1:")
    with transaktio(yhteys) as k:
        k.execute("UPDATE tili SET saldo = saldo - 30 WHERE nimi = 'Ada'")
        k.execute("UPDATE tili SET saldo = saldo + 30 WHERE nimi = 'Bob'")

    print("siirto 2:")
    try:
        with transaktio(yhteys) as k:
            k.execute("UPDATE tili SET saldo = saldo - 500 "
                      "WHERE nimi = 'Ada'")
            raise ValueError("kate ei riitä")
    except ValueError as virhe:
        print(f"  virhe: {virhe}")

    print(yhteys.execute("SELECT * FROM tili ORDER BY nimi").fetchall())
# @loppu kaytto
