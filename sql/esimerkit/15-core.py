"""Kyselynrakentaja: SQLAlchemy Core.

Kysely rakennetaan Python-olioista, ja SQLAlchemy kirjoittaa siitä
kunkin tietokannan murretta. Sama kysely käännetään SQLiten,
PostgreSQL:n ja MariaDB:n SQL:ksi ja ajetaan lopuksi SQLitessä.
"""

import re
from typing import Any

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Select,
    String,
    Table,
    create_engine,
    func,
    insert,
    select,
)
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.engine import Dialect

# PostgreSQL-murteen muodostimella ei ole tyyppimerkintöjä.
MURTEET: list[tuple[str, Dialect]] = [
    ("SQLite", sqlite.dialect()),
    ("PostgreSQL", postgresql.dialect()),  # type: ignore[no-untyped-call]
    ("MariaDB", mysql.dialect(is_mariadb=True)),
]

# @alku taulut
metatiedot = MetaData()
asiakas = Table(
    "asiakas", metatiedot,
    Column("id", Integer, primary_key=True),
    Column("nimi", String(80), nullable=False))
tilaus = Table(
    "tilaus", metatiedot,
    Column("id", Integer, primary_key=True),
    Column("asiakas_id", ForeignKey("asiakas.id"), nullable=False),
    Column("summa", Integer, nullable=False))
# @loppu taulut

# @alku kysely
def suurimmat(vahintaan: int, n: int) -> Select[Any]:
    """Asiakkaat, joiden tilausten summa on vähintään raja."""
    yhteensa = func.sum(tilaus.c.summa).label("yhteensa")
    return (select(asiakas.c.nimi, yhteensa)
            .join(tilaus, tilaus.c.asiakas_id == asiakas.c.id)
            .group_by(asiakas.c.id, asiakas.c.nimi)
            .having(yhteensa >= vahintaan)
            .order_by(yhteensa.desc(), asiakas.c.nimi)
            .limit(n))
# @loppu kysely


def siisti(sql: str) -> str:
    """Rivittää käännetyn SQL:n avainsanojen kohdalta luettavaksi."""
    sql = " ".join(sql.split())
    return re.sub(r" (FROM|(?:INNER )?JOIN|GROUP BY|HAVING|ORDER BY|LIMIT) ",
                  r"\n\1 ", sql)


def main() -> None:
    kysely = suurimmat(100, 2)
    # @alku murteet
    for nimi, murre in MURTEET:
        print(f"-- {nimi}")
        print(siisti(str(kysely.compile(dialect=murre))))
    # @loppu murteet

    # @alku ajo
    moottori = create_engine("sqlite://")
    metatiedot.create_all(moottori)
    with moottori.begin() as yhteys:
        yhteys.execute(insert(asiakas), [
            {"id": 1, "nimi": "Aino"}, {"id": 2, "nimi": "Matti"},
            {"id": 3, "nimi": "Liisa"}])
        yhteys.execute(insert(tilaus), [
            {"asiakas_id": 1, "summa": 120}, {"asiakas_id": 2, "summa": 40},
            {"asiakas_id": 3, "summa": 90}, {"asiakas_id": 3, "summa": 30}])
        for rivi in yhteys.execute(kysely):
            print(f"{rivi.nimi}: {rivi.yhteensa}")
    # @loppu ajo


if __name__ == "__main__":
    main()
