"""Lukemien yhteenvedot."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from saa.lukema import Lukema


# @alku keskiarvo
def liukuva_keskiarvo(arvot: Sequence[float], ikkuna: int) -> list[float]:
    """Laskee liukuvan keskiarvon.

    Tuloksen alkio ``i`` on arvojen ``arvot[i : i + ikkuna]`` keskiarvo,
    joten tulos on ``ikkuna - 1`` alkiota syötettä lyhyempi. Vajaita
    ikkunoita ei lasketa, koska ne näyttäisivät kuvaajassa
    muutokselta, jota mittauksissa ei ole.

    Args:
        arvot: Mittausarvot aikajärjestyksessä.
        ikkuna: Keskiarvoon otettavien arvojen määrä, vähintään 1.

    Returns:
        Keskiarvot. Lista on tyhjä, jos arvoja on vähemmän kuin
        ``ikkuna``.

    Raises:
        ValueError: Jos ``ikkuna`` on pienempi kuin 1.

    Example:
        >>> liukuva_keskiarvo([1.0, 2.0, 6.0, 3.0], ikkuna=2)
        [1.5, 4.0, 4.5]
    """
    if ikkuna < 1:
        raise ValueError("ikkunan on oltava vähintään 1")
    return [sum(arvot[i:i + ikkuna]) / ikkuna
            for i in range(len(arvot) - ikkuna + 1)]
# @loppu keskiarvo


@dataclass(frozen=True)
class Yhteenveto:
    """Yhden aseman lukemien tunnusluvut.

    Attributes:
        asema: Aseman tunnus.
        maara: Lukemien määrä.
        alin_c: Alin lämpötila celsiusasteina.
        ylin_c: Ylin lämpötila celsiusasteina.
        keskiarvo_c: Lämpötilojen keskiarvo yhden desimaalin
            tarkkuudella.
    """

    asema: str
    maara: int
    alin_c: float
    ylin_c: float
    keskiarvo_c: float


def yhteenveto(asema: str, lukemat: Sequence[Lukema]) -> Yhteenveto | None:
    """Laskee aseman lukemista yhteenvedon.

    Args:
        asema: Aseman tunnus. Muiden asemien lukemat ohitetaan.
        lukemat: Lukemat missä tahansa järjestyksessä.

    Returns:
        Yhteenveto tai ``None``, jos asemalta ei ole yhtään lukemaa.

    Example:
        >>> from saa.lukema import jasenna_rivi
        >>> rivit = ["kumpula;2026-11-25T12:00:00+02:00;-3.5;81",
        ...          "kumpula;2026-11-25T13:00:00+02:00;-1.5;"]
        >>> yhteenveto("kumpula", [jasenna_rivi(r) for r in rivit])
        ... # doctest: +NORMALIZE_WHITESPACE
        Yhteenveto(asema='kumpula', maara=2, alin_c=-3.5, ylin_c=-1.5,
                   keskiarvo_c=-2.5)
    """
    lammot = [x.lampotila_c for x in lukemat if x.asema == asema]
    if not lammot:
        return None
    return Yhteenveto(asema, len(lammot), min(lammot), max(lammot),
                      round(sum(lammot) / len(lammot), 1))
