"""Kiinteän pilkun perusoperaatiot sellaisina kuin RTL ne tekee.

Pythonin kokonaisluvut ovat rajattomia, joten jokainen bittileveyden
rajaus tehdään näkyvästi: saturoi() tai kierra(). Oikealle siirto >>
on Pythonissa aritmeettinen (pyöristää kohti miinus ääretöntä), kuten
SystemVerilogin >>> etumerkilliselle luvulle.
"""

from __future__ import annotations

import math


# @alku alue
def alue(bitit: int) -> tuple[int, int]:
    """Etumerkillisen bitit-levyisen luvun pienin ja suurin arvo."""
    return -(1 << (bitit - 1)), (1 << (bitit - 1)) - 1


def saturoi(arvo: int, bitit: int) -> int:
    """Rajaa arvon alueelle: ylivuoto jää suurimpaan arvoon."""
    pienin, suurin = alue(bitit)
    return min(max(arvo, pienin), suurin)


def kierra(arvo: int, bitit: int) -> int:
    """Kahden komplementin kierto: ylimmät bitit vain jätetään pois."""
    maski = (1 << bitit) - 1
    arvo &= maski
    return arvo - (1 << bitit) if arvo >> (bitit - 1) else arvo
    # @loppu alue


# @alku pyoristys
def katkaise(arvo: int, siirto: int) -> int:
    """Pudottaa siirto alinta bittiä (pyöristys kohti miinus ääretöntä)."""
    return arvo >> siirto


def pyorista(arvo: int, siirto: int) -> int:
    """Pyöristää lähimpään, puolikkaat ylöspäin: lisätään puolikas ja
    katkaistaan. Laitteistossa yksi summain ennen siirtoa."""
    if siirto == 0:
        return arvo
    return (arvo + (1 << (siirto - 1))) >> siirto
    # @loppu pyoristys


# @alku ulostulo
def ulostulo(
    arvo: int,
    siirto: int,
    bitit: int,
    pyoristys: bool = True,
    saturaatio: bool = True,
) -> int:
    """Leveä summa kapeaksi ulostuloksi: pyöristys tai katkaisu ja
    saturaatio tai kierto. Vastaa RTL-moduulia rtl/kavenna.sv."""
    lyhyt = pyorista(arvo, siirto) if pyoristys else katkaise(arvo, siirto)
    return saturoi(lyhyt, bitit) if saturaatio else kierra(lyhyt, bitit)
    # @loppu ulostulo


# @alku kvantisointi
def kvantisoi(x: float, murtobitit: int, bitit: int) -> int:
    """Liukuluku Q-muotoon: kerrotaan, pyöristetään lähimpään
    (puolikkaat ylöspäin) ja saturoidaan."""
    return saturoi(math.floor(x * (1 << murtobitit) + 0.5), bitit)


def liukuluvuksi(koodi: int, murtobitit: int) -> float:
    """Q-muotoinen kokonaisluku takaisin liukuluvuksi."""
    return koodi / (1 << murtobitit)
    # @loppu kvantisointi


# @alku leveys
def leveys(pienin: int, suurin: int) -> int:
    """Pienin etumerkillinen bittileveys, johon välin arvot mahtuvat."""
    bitit = 1
    while not (-(1 << (bitit - 1)) <= pienin and suurin < (1 << (bitit - 1))):
        bitit += 1
    return bitit
    # @loppu leveys
