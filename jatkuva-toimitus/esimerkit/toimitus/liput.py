"""Ominaisuusliput: käyttöönotto ja julkaisu erotetaan toisistaan.

Koodi viedään tuotantoon lipun takana pois päältä. Ominaisuus avataan
myöhemmin asetusta muuttamalla: ensin omalle väelle, sitten kasvavalle
osuudelle käyttäjistä.
"""

import hashlib
from dataclasses import dataclass
from datetime import date


# @alku lippu
@dataclass(frozen=True)
class Lippu:
    nimi: str
    omistaja: str
    luotu: date
    osuus: int = 0                              # prosenttia käyttäjistä
    sallitut: frozenset[str] = frozenset()      # aina päällä näille
    hatakatkaisu: bool = False                  # pois kaikilta heti
    pysyva: bool = False                        # operointilippu, ei poisteta


def lokero(lippu: str, kayttaja: str) -> int:
    """Käyttäjän pysyvä lokero 0-99 tälle lipulle.

    Tiiviste lasketaan lipun nimestä ja käyttäjästä, joten sama käyttäjä
    saa aina saman vastauksen eikä eri lippujen jako riipu toisistaan.
    """
    tavut = hashlib.sha256(f"{lippu}:{kayttaja}".encode()).digest()
    return int.from_bytes(tavut[:8], "big") % 100


def paalla(lippu: Lippu, kayttaja: str) -> bool:
    if lippu.hatakatkaisu:
        return False
    if kayttaja in lippu.sallitut:
        return True
    return lokero(lippu.nimi, kayttaja) < lippu.osuus
# @loppu lippu


# @alku velka
def poistettavat(liput: list[Lippu], tanaan: date,
                 raja_paivia: int = 30) -> list[Lippu]:
    """Liput, jotka ovat olleet kokonaan päällä tai pois liian kauan.

    Valmiiksi avattu lippu on kuollutta koodia: haara, jota ei enää
    valita, mutta joka on yhä luettava, testattava ja ylläpidettävä.
    """
    return [lippu for lippu in liput
            if lippu.osuus in (0, 100) and not lippu.pysyva
            and (tanaan - lippu.luotu).days > raja_paivia]
# @loppu velka
