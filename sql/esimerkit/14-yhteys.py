"""Yhteys, kysely ja tulokset Pythonin DB-API:lla (sqlite3)."""

import sqlite3
from contextlib import closing
from datetime import date


# @alku avaa
def avaa(polku: str) -> sqlite3.Connection:
    """Avaa yhteyden aina samoilla asetuksilla."""
    yhteys = sqlite3.connect(polku, autocommit=False, timeout=5)
    yhteys.execute("PRAGMA foreign_keys = ON")
    # Sarakkeisiin viitataan nimellä: rivi["nimi"] eikä rivi[1].
    yhteys.row_factory = sqlite3.Row
    return yhteys
# @loppu avaa


def alusta(yhteys: sqlite3.Connection) -> None:
    yhteys.executescript("""
        CREATE TABLE tuote (
            id        INTEGER PRIMARY KEY,
            nimi      TEXT NOT NULL UNIQUE,
            hinta_snt INTEGER NOT NULL CHECK (hinta_snt >= 0),
            paino_kg  REAL,
            lisatty   TEXT NOT NULL CHECK (lisatty = date(lisatty))
        ) STRICT;
        INSERT INTO tuote (nimi, hinta_snt, paino_kg, lisatty) VALUES
            ('Kahvi 500 g', 899, 0.5, '2026-09-01'),
            ('Teekannu', 2490, NULL, '2026-10-15'),
            ('Suklaa', 349, 0.2, '2026-11-02');
    """)
    yhteys.commit()


def main() -> None:
    # closing sulkee yhteyden lohkon lopussa myös virheen sattuessa.
    with closing(avaa(":memory:")) as yhteys:
        alusta(yhteys)

        # @alku kysely
        kursori = yhteys.execute(
            "SELECT id, nimi, hinta_snt FROM tuote ORDER BY hinta_snt")
        for rivi in kursori:             # rivit luetaan yksi kerrallaan
            print(f"{rivi['id']}: {rivi['nimi']}, "
                  f"{rivi['hinta_snt'] / 100:.2f} e")
        # @loppu kysely

        # @alku yksi
        rivi = yhteys.execute(
            "SELECT count(*) AS n, max(hinta_snt) AS kallein "
            "FROM tuote").fetchone()
        print("tuotteita:", rivi["n"], "kallein:", rivi["kallein"])
        puuttuva = yhteys.execute(
            "SELECT nimi FROM tuote WHERE id = 99").fetchone()
        print("id 99:", puuttuva)        # ei riviä: None
        # @loppu yksi

        # @alku tyypit
        rivi = yhteys.execute(
            "SELECT hinta_snt, paino_kg, nimi, lisatty "
            "FROM tuote WHERE nimi = 'Teekannu'").fetchone()
        for sarake, arvo in zip(rivi.keys(), rivi, strict=True):
            print(f"{sarake}: {arvo!r} ({type(arvo).__name__})")
        # SQLitessä päivämäärä on tekstiä; muunnos tehdään reunalla.
        lisatty = date.fromisoformat(rivi["lisatty"])
        print("viikonpäivä:", lisatty.isoweekday())
        # @loppu tyypit

        # @alku muutos
        kursori = yhteys.execute(
            "INSERT INTO tuote (nimi, hinta_snt, lisatty) "
            "VALUES ('Muki', 1290, '2026-11-20')")
        print("uusi id:", kursori.lastrowid)
        kursori = yhteys.execute(
            "UPDATE tuote SET hinta_snt = hinta_snt + 100 "
            "WHERE hinta_snt < 1000")
        print("muuttui:", kursori.rowcount, "riviä")
        yhteys.commit()                  # ilman tätä muutokset katoavat
        # @loppu muutos


if __name__ == "__main__":
    main()
