"""Sama DB-API, kaksi ajuria: arvojen tyypit SQLitessä ja PostgreSQL:ssä.

Ilman ympäristömuuttujaa PG_DSN ajetaan vain sqlite3-osa. Testiajo
(palvelimet/aja.sh) antaa PostgreSQL-yhteyden, jolloin sama tehtävä
ajetaan myös psycopg-ajurilla.
"""

import os
import sqlite3
from datetime import UTC, date, datetime
from decimal import Decimal

import psycopg


def nayta(sarakkeet: list[str], rivi: tuple[object, ...]) -> None:
    for sarake, arvo in zip(sarakkeet, rivi, strict=True):
        print(f"  {sarake}: {arvo} ({type(arvo).__name__})")


# @alku sqlite
def sqlite_ajo() -> None:
    print(f"sqlite3 (paramstyle {sqlite3.paramstyle})")
    yhteys = sqlite3.connect(":memory:", autocommit=False)
    yhteys.execute("""
        CREATE TABLE tarjous (
            hinta_snt INTEGER NOT NULL,
            paiva     TEXT NOT NULL,
            voimassa  INTEGER NOT NULL,
            luotu     TEXT NOT NULL
        ) STRICT""")
    # Sovellus muuntaa arvot SQLiten neljään perustyyppiin itse.
    yhteys.execute(
        "INSERT INTO tarjous VALUES (?, ?, ?, ?)",
        (1290, date(2026, 11, 20).isoformat(), int(True),
         datetime(2026, 11, 20, 8, 30, tzinfo=UTC).isoformat()))
    kursori = yhteys.execute("SELECT * FROM tarjous")
    nayta([s[0] for s in kursori.description], kursori.fetchone())
    yhteys.close()
# @loppu sqlite


# @alku postgres
def postgres_ajo(dsn: str) -> None:
    print(f"psycopg (paramstyle {psycopg.paramstyle})")
    with psycopg.connect(dsn) as yhteys:
        yhteys.execute("""
            CREATE TEMP TABLE tarjous (
                hinta    numeric(10,2) NOT NULL,
                paiva    date NOT NULL,
                voimassa boolean NOT NULL,
                luotu    timestamptz NOT NULL
            )""")
        # Ajuri muuntaa Pythonin tyypit tietokannan tyypeiksi ja takaisin.
        yhteys.execute(
            "INSERT INTO tarjous VALUES (%s, %s, %s, %s)",
            (Decimal("12.90"), date(2026, 11, 20), True,
             datetime(2026, 11, 20, 8, 30, tzinfo=UTC)))
        kursori = yhteys.execute("SELECT * FROM tarjous")
        rivi = kursori.fetchone()
        assert rivi is not None and kursori.description is not None
        nayta([s.name for s in kursori.description], rivi)
# @loppu postgres


def main() -> None:
    sqlite_ajo()
    dsn = os.environ.get("PG_DSN")
    if dsn:
        postgres_ajo(dsn)


if __name__ == "__main__":
    main()
