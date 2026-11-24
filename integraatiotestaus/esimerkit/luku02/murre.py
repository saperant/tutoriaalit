"""Sama skeema ja samat lauseet SQLitessä ja PostgreSQLissä.

Yksikkötesti SQLitellä menisi läpi, vaikka tuotannon PostgreSQL
hylkäisi rivit, tai päinvastoin. Ajetaan molemmat ja verrataan."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import DBAPIError

from testiapu import kontit

# @alku lauseet
SKEEMA = """CREATE TABLE tuotteet (
    sku   varchar(8) PRIMARY KEY,
    nimi  text NOT NULL,
    saldo integer NOT NULL)"""

KOKEET = [
    ("liian pitkä sku",
     "INSERT INTO tuotteet VALUES ('ABC-123456', 'Ruuvi', 1)"),
    ("tekstiä lukukenttään",
     "INSERT INTO tuotteet VALUES ('ABC-2', 'Mutteri', 'paljon')"),
    ("LIKE ja kirjainkoko",
     "SELECT 'abc' LIKE 'ABC'"),
    ("teksti '1' = luku 1",
     "SELECT '1' = 1"),
    ("lajittelu, NULL viimeisenä?",
     "SELECT x FROM (SELECT 1 AS x UNION ALL SELECT NULL) t ORDER BY x"),
]
# @loppu lauseet


def kokeile(kone: Engine, lause: str) -> str:
    try:
        with kone.begin() as y:
            tulos = y.execute(text(lause))
            if not tulos.returns_rows:
                return "hyväksyttiin"
            return " ".join(str(r[0]) for r in tulos)
    except DBAPIError as e:
        return "virhe: " + type(e.orig).__name__


def main() -> None:
    sqlite = create_engine("sqlite://")
    with kontit.postgres() as pg:
        postgres = create_engine(pg.get_connection_url())
        for kone in (sqlite, postgres):
            with kone.begin() as y:
                y.execute(text(SKEEMA))
        print(f"{'koe':<28}{'SQLite':<16}PostgreSQL")
        for nimi, lause in KOKEET:
            print(f"{nimi:<28}{kokeile(sqlite, lause):<16}"
                  f"{kokeile(postgres, lause)}")
        postgres.dispose()


if __name__ == "__main__":
    main()
