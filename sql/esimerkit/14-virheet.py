"""Tietokantavirheet sovelluksessa: rajoitevirhe sovelluksen virheeksi
ja tilapäisen lukitusvirheen uudelleenyritys."""

import sqlite3
from collections.abc import Callable


class SahkopostiVarattu(Exception):
    """Sovelluksen oma virhe: käyttäjälle näytettävä tilanne."""


def avaa(polku: str) -> sqlite3.Connection:
    # timeout=0: lukkoa ei odoteta, jotta lukitusvirhe näkyy heti.
    return sqlite3.connect(polku, autocommit=False, timeout=0)


# @alku rajoite
def rekisteroi(yhteys: sqlite3.Connection, sahkoposti: str) -> int:
    """Lisää käyttäjän ja palauttaa tunnisteen."""
    try:
        with yhteys:
            kursori = yhteys.execute(
                "INSERT INTO kayttaja (sahkoposti) VALUES (?)",
                (sahkoposti,))
    except sqlite3.IntegrityError as virhe:
        # Vain tunnettu rajoite muunnetaan; muut virheet jatkavat ylös.
        if virhe.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
            raise SahkopostiVarattu(sahkoposti) from virhe
        raise
    assert kursori.lastrowid is not None
    return kursori.lastrowid
# @loppu rajoite


# @alku uudelleen
def yrita[T](toiminto: Callable[[], T], yrityksia: int,
             odota: Callable[[int], None]) -> T:
    """Ajaa transaktion uudelleen, jos tietokanta oli varattu."""
    for kerta in range(1, yrityksia + 1):
        try:
            return toiminto()
        except sqlite3.OperationalError as virhe:
            tilapainen = virhe.sqlite_errorname in (
                "SQLITE_BUSY", "SQLITE_LOCKED")
            if not tilapainen or kerta == yrityksia:
                raise
            odota(kerta)
    raise AssertionError("ei saavuteta")
# @loppu uudelleen


def main() -> None:
    a = avaa("kayttajat.db")
    a.executescript("""
        CREATE TABLE kayttaja (
            id         INTEGER PRIMARY KEY,
            sahkoposti TEXT NOT NULL UNIQUE
                       CHECK (sahkoposti LIKE '%_@_%')
        ) STRICT;""")
    a.commit()

    # @alku kaytto
    print("lisätty:", rekisteroi(a, "aino@example.com"))
    try:
        rekisteroi(a, "aino@example.com")
    except SahkopostiVarattu as virhe:
        print("varattu:", virhe)
    try:
        rekisteroi(a, "ei-osoite")
    except sqlite3.IntegrityError as virhe:
        print("muu rajoite:", virhe.sqlite_errorname)
    # @loppu kaytto

    # @alku lukitus
    b = sqlite3.connect("kayttajat.db", autocommit=True, timeout=0)
    b.execute("BEGIN IMMEDIATE")         # toinen yhteys kirjoittaa

    def vapauta(kerta: int) -> None:
        # Oikeassa sovelluksessa tässä odotettaisiin hetki (kasvava
        # viive ja satunnaisuutta); esimerkissä toinen yhteys sitoutuu.
        print(f"yritys {kerta}: tietokanta varattu, yritetään uudelleen")
        b.execute("COMMIT")

    tunniste = yrita(lambda: rekisteroi(a, "matti@example.com"),
                     yrityksia=3, odota=vapauta)
    print("lisätty:", tunniste)
    # @loppu lukitus
    a.close()
    b.close()


if __name__ == "__main__":
    main()
