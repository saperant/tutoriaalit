"""Toistettujen simulointien tunnusluvut ja luottamusvälit."""

import math
import statistics
from collections.abc import Sequence

# @alku t
# Studentin t-jakauman 97,5 %:n kvantiilit (kaksisuuntainen 95 %:n
# luottamusväli) vapausasteille 1-30; suuremmilla käytetään 1,96:ta.
_T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262,
         2.228, 2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101,
         2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052,
         2.048, 2.045, 2.042]


def t975(vapausasteet: int) -> float:
    if vapausasteet < 1:
        raise ValueError("vähintään kaksi toistoa")
    return _T975[vapausasteet - 1] if vapausasteet <= 30 else 1.96


def luottamusvali(arvot: Sequence[float]) -> tuple[float, float]:
    """Keskiarvo ja 95 %:n luottamusvälin puolileveys riippumattomista
    toistoista (eri siemenet)."""
    ka = statistics.fmean(arvot)
    s = statistics.stdev(arvot)
    return ka, t975(len(arvot) - 1) * s / math.sqrt(len(arvot))


def toistoja_tarvitaan(arvot: Sequence[float], suhteellinen: float) -> int:
    """Arvio toistojen määrästä, jolla puolileveys on enintään
    suhteellinen * keskiarvo (normaaliapproksimaatio)."""
    ka, s = statistics.fmean(arvot), statistics.stdev(arvot)
    return math.ceil((1.96 * s / (suhteellinen * ka)) ** 2)
# @loppu t


# @alku virheet
def virheet(ennuste: Sequence[float], viite: Sequence[float]
            ) -> tuple[float, float]:
    """Keskimääräinen suhteellinen itseisvirhe (MAPE) ja suurin
    suhteellinen virhe."""
    e = [abs(p / v - 1) for p, v in zip(ennuste, viite, strict=True)]
    return statistics.fmean(e), max(e)
# @loppu virheet
