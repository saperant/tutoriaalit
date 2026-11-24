"""Kolme tapaa eristää testit samassa PostgreSQLissä."""

from __future__ import annotations

from sqlalchemy import Connection, Engine, create_engine, text

from testiapu import kontit
from testiapu.data import ainutlaatuinen, tuote
from varasto.migraatiot import migroi
from varasto.varasto import PgVarasto


def rivit(y: Connection) -> int:
    return int(y.execute(text("SELECT count(*) FROM tuotteet"))
               .scalar_one())


def laske(kone: Engine) -> int:
    with kone.connect() as y:
        return rivit(y)


# @alku peruutus
def peruutus(kone: Engine) -> None:
    """1. Transaktio perutaan testin lopuksi (nopein)."""
    with kone.connect() as y:
        transaktio = y.begin()
        PgVarasto(y).lisaa(tuote(1))
        print("  testin aikana:", rivit(y))
        transaktio.rollback()
    print("  testin jälkeen:", laske(kone))
# @loppu peruutus


# @alku tyhjennys
def tyhjennys(kone: Engine) -> None:
    """2. Testi kirjoittaa pysyvästi; taulut tyhjennetään jälkeenpäin.
    Tarvitaan, kun testattava koodi avaa omat yhteytensä."""
    PgVarasto(kone).lisaa(tuote(2))
    print("  testin aikana:", laske(kone))
    with kone.begin() as y:
        y.execute(text("TRUNCATE varaukset, tuotteet"))
    print("  testin jälkeen:", laske(kone))
# @loppu tyhjennys


# @alku pohja
def pohjasta(hallinta: Engine, perus_url: str) -> None:
    """3. Jokainen testi saa oman tietokannan kopiona migroidusta
    pohjasta. CREATE DATABASE ... TEMPLATE kopioi tiedostot, mikä on
    nopeampaa kuin migraatioiden ajaminen uudelleen."""
    nimi = ainutlaatuinen("testi").replace("-", "_")
    with hallinta.connect() as y:
        y.execute(text(f'CREATE DATABASE "{nimi}" TEMPLATE pohja'))
    oma = create_engine(f"{perus_url}/{nimi}")
    PgVarasto(oma).lisaa(tuote(3))
    print("  omassa kannassa:", laske(oma))
    oma.dispose()
    with hallinta.connect() as y:
        y.execute(text(f'DROP DATABASE "{nimi}"'))
# @loppu pohja


def main() -> None:
    with kontit.postgres() as pg:
        url = pg.get_connection_url()
        perus_url = url.rsplit("/", 1)[0]
        kone = create_engine(url)
        print("migraatiot:", ", ".join(migroi(kone)))
        print("1. peruutus")
        peruutus(kone)
        print("2. tyhjennys")
        tyhjennys(kone)
        # Pohjana ei saa olla avoimia yhteyksiä, joten allas suljetaan.
        kone.dispose()
        hallinta = create_engine(f"{perus_url}/postgres",
                                 isolation_level="AUTOCOMMIT")
        with hallinta.connect() as y:
            y.execute(text("CREATE DATABASE pohja TEMPLATE varasto"))
        print("3. pohjasta")
        pohjasta(hallinta, perus_url)
        pohjasta(hallinta, perus_url)
        hallinta.dispose()


if __name__ == "__main__":
    main()
