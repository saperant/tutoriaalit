"""Julkaisustrategioiden malli: kuinka moni pyyntö osuu vialliseen versioon.

Liikenne jaetaan vanhan ja uuden version kesken askel kerrallaan.
Valvonta seuraa uuden version virheosuutta ja peruu julkaisun, kun
osuus ylittää rajan. Strategiat eroavat siinä, kuinka suuri osa
liikenteestä uudelle versiolle annetaan ja kuinka nopeasti paluu käy.
"""

import random
from dataclasses import dataclass


# @alku strategia
@dataclass(frozen=True)
class Strategia:
    nimi: str
    portaat: tuple[float, ...]     # uuden version liikenneosuus askelittain
    paluu: tuple[float, ...]       # osuudet havainnon jälkeen, kunnes 0


STRATEGIAT = (
    # Kaikki palvelimet päivitetään kerralla; paluu on uusi asennus.
    Strategia("kerralla", (1.0,), (1.0, 1.0, 1.0)),
    # Palvelin kerrallaan; paluu samaa tietä takaisin.
    Strategia("rullaava", tuple(i / 10 for i in range(1, 11)), (0.1,)),
    # Uusi ympäristö rinnalle; liikenne käännetään kerralla ja takaisin.
    Strategia("sinivihreä", (1.0,), ()),
    # Pieni osuus ensin; osuutta kasvatetaan vain, jos mittarit pysyvät.
    Strategia("kanarialintu", (0.05, 0.05, 0.05, 0.25, 0.5, 1.0), ()),
)
# @loppu strategia


@dataclass(frozen=True)
class Asetelma:
    pyyntoja: int = 1000           # pyyntöä askeleessa
    virhe_uusi: float = 0.05       # uuden version virheosuus
    raja: float = 0.02             # valvonnan hälytysraja
    vahimmaisnayte: int = 100      # tätä pienemmästä näytteestä ei päätetä


@dataclass(frozen=True)
class Tulos:
    peruttu: bool
    askelia: int
    uudelle: int                   # uuden version palvelemat pyynnöt
    virheita: int                  # niistä epäonnistuneet
    kertyma: tuple[int, ...]       # virheet askelittain kertyneinä


# @alku simuloi
def simuloi(strategia: Strategia, asetelma: Asetelma,
            arpa: random.Random) -> Tulos:
    """Ajaa yhden julkaisun ja palauttaa, mitä käyttäjät kokivat."""
    uudelle = virheita = 0
    kertyma: list[int] = []

    def askel(osuus: float) -> None:
        nonlocal uudelle, virheita
        maara = round(asetelma.pyyntoja * osuus)
        uudelle += maara
        virheita += sum(arpa.random() < asetelma.virhe_uusi
                        for _ in range(maara))
        kertyma.append(virheita)

    for osuus in strategia.portaat:
        askel(osuus)
        if (uudelle >= asetelma.vahimmaisnayte
                and virheita / uudelle > asetelma.raja):
            for paluuosuus in strategia.paluu:    # paluu vie aikansa
                askel(paluuosuus)
            return Tulos(True, len(kertyma), uudelle, virheita,
                         tuple(kertyma))
    return Tulos(False, len(kertyma), uudelle, virheita, tuple(kertyma))
# @loppu simuloi


def keskiarvot(strategia: Strategia, asetelma: Asetelma, toistoja: int,
               siemen: int = 1) -> tuple[float, float, float, float]:
    """Perumisten osuus sekä askelten, pyyntöjen ja virheiden keskiarvot."""
    arpa = random.Random(siemen)
    tulokset = [simuloi(strategia, asetelma, arpa) for _ in range(toistoja)]
    return (sum(t.peruttu for t in tulokset) / toistoja,
            sum(t.askelia for t in tulokset) / toistoja,
            sum(t.uudelle for t in tulokset) / toistoja,
            sum(t.virheita for t in tulokset) / toistoja)
