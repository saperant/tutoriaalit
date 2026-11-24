"""Skeeman migraatiot: numeroidut SQL-tiedostot ajetaan järjestyksessä.

Ajetut migraatiot kirjataan tauluun skeemaversiot, joten migroi() on
turvallista kutsua uudelleen. Tuotannossa sama tehtävä hoidetaan
työkalulla (Alembic, Flyway, Liquibase); periaate on sama.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, text

HAKEMISTO = Path(__file__).parent / "migraatiot"


# @alku migroi
def migroi(kone: Engine) -> list[str]:
    """Ajaa puuttuvat migraatiot yhdessä transaktiossa.

    Palauttaa ajettujen tiedostojen nimet."""
    ajetut: list[str] = []
    with kone.begin() as yhteys:
        yhteys.execute(text(
            "CREATE TABLE IF NOT EXISTS skeemaversiot ("
            " nimi text PRIMARY KEY,"
            " ajettu timestamptz NOT NULL DEFAULT now())"))
        tehdyt: set[str] = set(yhteys.execute(
            text("SELECT nimi FROM skeemaversiot")).scalars())
        for tiedosto in sorted(HAKEMISTO.glob("*.sql")):
            if tiedosto.name in tehdyt:
                continue
            yhteys.exec_driver_sql(tiedosto.read_text("utf-8"))
            yhteys.execute(
                text("INSERT INTO skeemaversiot (nimi) VALUES (:n)"),
                {"n": tiedosto.name})
            ajetut.append(tiedosto.name)
    return ajetut
# @loppu migroi
