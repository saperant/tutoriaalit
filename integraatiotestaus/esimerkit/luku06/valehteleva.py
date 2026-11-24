"""Kun väärennös valehtelee: naiivi muistitoteutus läpäisee testit,
jotka oikea PostgreSQL hylkää."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import create_engine

from testiapu import kontit
from varasto.malli import SaldoEiRiita, SkuVarattu, Tuote, Varaus
from varasto.migraatiot import migroi
from varasto.varasto import PgVarasto, Varasto


# @alku naiivi
class NaiiviVarasto:
    """Ensimmäinen väärennös, joka kirjoitettiin "nopeasti testejä
    varten". Se näyttää oikealta mutta tekee kolme oletusta, joita
    tietokanta ei tee."""

    def __init__(self) -> None:
        self.tuotteet: dict[str, Tuote] = {}
        self.lista: list[Varaus] = []

    def lisaa(self, tuote: Tuote) -> None:
        if tuote.sku in self.tuotteet:        # kirjainkoko ratkaisee
            raise SkuVarattu(tuote.sku)
        self.tuotteet[tuote.sku] = tuote

    def hae(self, sku: str) -> Tuote | None:
        return self.tuotteet.get(sku)         # kirjainkoko ratkaisee

    def varaa(self, sku: str, maara: int) -> Varaus:
        tuote = self.tuotteet.get(sku)
        if tuote is None or tuote.saldo < maara:
            raise SaldoEiRiita(sku)
        self.tuotteet[sku] = Tuote(sku, tuote.nimi, tuote.saldo - maara)
        varaus = Varaus(len(self.lista) + 1, sku, maara,
                        datetime.now())       # ilman aikavyöhykettä
        self.lista.append(varaus)
        return varaus

    def varaukset(self, sku: str) -> list[Varaus]:
        return [v for v in self.lista if v.sku == sku]
# @loppu naiivi


def kokeet(v: Varasto) -> list[str]:
    tulokset = []
    v.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    tulokset.append("löytyi" if v.hae("abc-1") else "ei löytynyt")
    try:
        v.lisaa(Tuote("abc-1", "Ruuvi", 5))
        tulokset.append("hyväksyttiin")
    except SkuVarattu:
        tulokset.append("SkuVarattu")
    vyohyke = v.varaa("ABC-1", 1).luotu.tzinfo
    tulokset.append("ei ole" if vyohyke is None else str(vyohyke))
    return tulokset


def main() -> None:
    naiivi = kokeet(NaiiviVarasto())
    with kontit.postgres() as pg:
        kone = create_engine(pg.get_connection_url())
        migroi(kone)
        with kone.connect() as y:
            oikea = kokeet(PgVarasto(y))
            y.rollback()
        kone.dispose()
    nimet = ["hae('abc-1')", "'ABC-1' ja 'abc-1'", "varauksen vyöhyke"]
    print(f"{'koe':<22}{'naiivi väärennös':<20}PostgreSQL")
    for nimi, a, b in zip(nimet, naiivi, oikea, strict=True):
        print(f"{nimi:<22}{a:<20}{b}")


if __name__ == "__main__":
    main()
