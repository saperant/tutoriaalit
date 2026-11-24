"""ORM: SQLAlchemy ORM, työyksikkö, identiteettikartta ja N+1.

Tietokannan osoite luetaan ympäristömuuttujasta TIETOKANTA; oletus on
SQLite muistissa. Testiajo ajaa saman ohjelman myös PostgreSQL:ää ja
MariaDB:tä vasten, ja tulosteen on oltava sama.
"""

import os
from typing import Any

from sqlalchemy import ForeignKey, String, create_engine, event, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)


# @alku mallit
class Malli(DeclarativeBase):
    pass


class Asiakas(Malli):
    __tablename__ = "asiakas"
    id: Mapped[int] = mapped_column(primary_key=True)
    nimi: Mapped[str] = mapped_column(String(80))
    tilaukset: Mapped[list["Tilaus"]] = relationship(
        back_populates="asiakas", order_by="Tilaus.id")


class Tilaus(Malli):
    __tablename__ = "tilaus"
    id: Mapped[int] = mapped_column(primary_key=True)
    asiakas_id: Mapped[int] = mapped_column(ForeignKey("asiakas.id"))
    summa: Mapped[int]
    asiakas: Mapped[Asiakas] = relationship(back_populates="tilaukset")
# @loppu mallit


class Laskuri:
    """Laskee tietokantaan lähetetyt SELECT-lauseet."""

    def __init__(self) -> None:
        self.kyselyja = 0

    def __call__(self, *args: Any) -> None:
        lause = str(args[2])
        if lause.lstrip().upper().startswith("SELECT"):
            self.kyselyja += 1


def main() -> None:
    moottori = create_engine(os.environ.get("TIETOKANTA", "sqlite://"))
    Malli.metadata.drop_all(moottori)
    Malli.metadata.create_all(moottori)

    # @alku tyoyksikko
    with Session(moottori) as istunto, istunto.begin():
        for i, nimi in enumerate(["Aino", "Matti", "Liisa"], start=1):
            asiakas = Asiakas(id=i, nimi=nimi)
            asiakas.tilaukset = [Tilaus(summa=10 * i * k)
                                 for k in range(1, 3)]
            istunto.add(asiakas)
        # Mitään ei ole vielä lähetetty: begin()-lohkon loppu kirjoittaa
        # kaikki muutokset yhdessä transaktiossa (työyksikkö).
        print("odottaa:", len(istunto.new), "uutta oliota")
    # @loppu tyoyksikko

    laskuri = Laskuri()
    event.listen(moottori, "before_cursor_execute", laskuri)

    # @alku identiteetti
    with Session(moottori) as istunto:
        a = istunto.get(Asiakas, 1)
        b = istunto.scalars(select(Asiakas).where(Asiakas.nimi == "Aino")
                            ).one()
        print("sama olio:", a is b)
    # @loppu identiteetti

    # @alku n-plus-1
    with Session(moottori) as istunto:
        laskuri.kyselyja = 0
        for asiakas in istunto.scalars(select(Asiakas).order_by(Asiakas.id)):
            summa = sum(t.summa for t in asiakas.tilaukset)  # laiska lataus
            print(f"{asiakas.nimi}: {summa}")
        print("kyselyjä laiskalla latauksella:", laskuri.kyselyja)

    with Session(moottori) as istunto:
        laskuri.kyselyja = 0
        kysely = (select(Asiakas).order_by(Asiakas.id)
                  .options(selectinload(Asiakas.tilaukset)))
        for asiakas in istunto.scalars(kysely):
            sum(t.summa for t in asiakas.tilaukset)
        print("kyselyjä ennakkolatauksella:", laskuri.kyselyja)
    # @loppu n-plus-1

    event.remove(moottori, "before_cursor_execute", laskuri)
    Malli.metadata.drop_all(moottori)


if __name__ == "__main__":
    main()
