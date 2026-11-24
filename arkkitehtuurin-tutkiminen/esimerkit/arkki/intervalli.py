"""Intervallimalli ja SimPoint-tyylinen näytteistys.

Käskyvirta on merkkijono, jonka merkit ovat 06-ydin-esimerkin tyypit:
a laskenta, l välimuistiosuma, m riippumaton huti, d huti, joka riippuu
edellisestä latauksesta, b oikein ja x väärin ennustettu haara.
"""

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass


# @alku intervalli
@dataclass(frozen=True)
class Ydin:
    ikkuna: int  # ROB, käskyä
    perus_cpi: float  # CPI ilman hutia ja väärää ennustusta
    huti: int = 97  # hudin lisäviive osumaan verrattuna, jaksoa
    haara: int = 18  # väärän ennustuksen hinta: palautus + ratkaisu


def intervallimalli(kaskyt: str, ydin: Ydin, limitys: bool = True,
                    riippuvuudet: bool = True) -> float:
    """Arvioi jaksot. Suoritus etenee perusnopeudella, kunnes jokin
    tapahtuma (huti tai väärä ennustus) katkaisee sen; kunkin
    tapahtuman hinta lisätään. Huti, joka on enintään ikkunan
    päässä edellisestä johtavasta hudista, limittyy sen kanssa eikä
    maksa mitään. Riippuva huti ei voi alkaa ennen edellistä, joten se
    maksaa aina koko viiveen."""
    jaksot = len(kaskyt) * ydin.perus_cpi
    johtava = -math.inf  # edellisen johtavan hudin paikka
    for i, k in enumerate(kaskyt):
        if k == "x":
            jaksot += ydin.haara
        elif k == "m" or (k == "d" and not riippuvuudet):
            if limitys and i - johtava < ydin.ikkuna:
                continue  # piiloutuu johtavan hudin varjoon
            jaksot += ydin.huti
            johtava = i
        elif k == "d":
            jaksot += ydin.huti
            johtava = i
    return jaksot
# @loppu intervalli


# @alku kmeans
def _etaisyys2(a: Sequence[float], b: Sequence[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True))


def kmeans(pisteet: Sequence[Sequence[float]], k: int, siemen: int,
           kierroksia: int = 50) -> list[int]:
    """k-means++-alustus (Arthur ja Vassilvitskii 2007) ja Lloydin
    iteraatio. Palauttaa kunkin pisteen ryhmän."""
    sat = random.Random(siemen)
    keskukset = [list(pisteet[sat.randrange(len(pisteet))])]
    while len(keskukset) < k:
        d2 = [min(_etaisyys2(p, c) for c in keskukset) for p in pisteet]
        raja, kertyma = sat.random() * sum(d2), 0.0
        for p, d in zip(pisteet, d2, strict=True):
            kertyma += d
            if kertyma >= raja:
                keskukset.append(list(p))
                break
    ryhmat = [0] * len(pisteet)
    for kierros in range(kierroksia):
        uudet = [min(range(k), key=lambda j: _etaisyys2(p, keskukset[j]))
                 for p in pisteet]
        if uudet == ryhmat and kierros > 0:
            break
        ryhmat = uudet
        for j in range(k):
            jasenet = [p for p, r in zip(pisteet, ryhmat, strict=True)
                       if r == j]
            if jasenet:
                keskukset[j] = [sum(x) / len(jasenet)
                                for x in zip(*jasenet, strict=True)]
    return ryhmat
# @loppu kmeans


# @alku simpoint
def simpoint(bbv: Sequence[Sequence[int]], cpi: Sequence[float], k: int,
             siemen: int = 1) -> tuple[float, list[int]]:
    """Ryhmittelee intervallit peruslohkovektorien perusteella ja
    valitsee kustakin ryhmästä keskusta lähimmän intervallin. Arvio on
    edustajien CPI:den painotettu keskiarvo (paino = ryhmän koko).
    Palauttaa arvion ja edustajien indeksit."""
    normitettu = [[x / sum(v) for x in v] for v in bbv]
    ryhmat = kmeans(normitettu, k, siemen)
    arvio, edustajat = 0.0, []
    for j in sorted(set(ryhmat)):
        jasenet = [i for i, r in enumerate(ryhmat) if r == j]
        keskus = [sum(normitettu[i][d] for i in jasenet) / len(jasenet)
                  for d in range(len(normitettu[0]))]
        edustaja = min(jasenet,
                       key=lambda i: _etaisyys2(normitettu[i], keskus))
        edustajat.append(edustaja)
        arvio += cpi[edustaja] * len(jasenet) / len(bbv)
    return arvio, edustajat
# @loppu simpoint
