"""Salaisuus ympäristöstä: ei oletusarvoa eikä näkymistä tulosteissa."""

import os
from dataclasses import dataclass


# @alku salaisuus
class Salaisuus:
    """Arvo saadaan vain nimenomaisesti; repr ja str eivät paljasta sitä,
    joten se ei vuoda lokeihin, virheilmoituksiin eikä debug-tulosteisiin."""

    def __init__(self, arvo: str) -> None:
        self._arvo = arvo

    def paljasta(self) -> str:
        return self._arvo

    def __repr__(self) -> str:
        return "Salaisuus('********')"

    __str__ = __repr__


def vaadi(nimi: str) -> Salaisuus:
    arvo = os.environ.get(nimi)
    if not arvo:
        # Ei oletusarvoa: puuttuva salaisuus pysäyttää käynnistyksen.
        raise SystemExit(f"ympäristömuuttuja {nimi} puuttuu")
    return Salaisuus(arvo)
# @loppu salaisuus


@dataclass(frozen=True)
class Tietokanta:
    osoite: str
    salasana: Salaisuus


os.environ["KANTA_SALASANA"] = "s3cr3t-arvo"   # tavallisesti ajoympäristö
asetukset = Tietokanta("db.sisainen:5432", vaadi("KANTA_SALASANA"))
print(asetukset)
print("pituus:", len(asetukset.salasana.paljasta()))
del os.environ["KANTA_SALASANA"]
try:
    vaadi("KANTA_SALASANA")
except SystemExit as e:
    print("käynnistys keskeytyy:", e)
