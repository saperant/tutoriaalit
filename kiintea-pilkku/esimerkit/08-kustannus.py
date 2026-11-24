"""Karkea pinta-alamalli: kiinteän pilkun ja liukuluvun aritmetiikka.

Yksikkönä on yksi täyssummain tai 2:1-multiplekseri (suunnilleen yhtä
suuret). Malli ei korvaa synteesiä, mutta näyttää mittasuhteet.
"""

import math


# @alku malli
def summain(n: int) -> float:
    return n                                    # n täyssummainta


def kertoja(n: int) -> float:
    return n * n                                # taulukkokertoja ~ n^2


def siirtaja(n: int) -> float:
    return n * math.ceil(math.log2(n))          # log2(n) muxikerrosta


def liuku_summain(e: int, m: int) -> float:
    """Eksponenttien vertailu, kohdistus, summa, normalisointi
    (etunollien laskenta ja siirto) sekä pyöristys."""
    return (summain(e) + siirtaja(m + 3) + summain(m + 3) + (m + 3)
            + siirtaja(m + 3) + summain(m))


def liuku_kertoja(e: int, m: int) -> float:
    """Mantissojen tulo, eksponenttien summa, normalisointi (tulo on
    välillä [1, 4), joten riittää yhden bitin siirto) ja pyöristys."""
    return kertoja(m) + summain(e) + m + summain(m)
# @loppu malli


# @alku taulukko
rivit = [
    ("kiinteä 16 b", summain(16), kertoja(16)),
    ("kiinteä 32 b", summain(32), kertoja(32)),
    ("binary16 (e5, m11)", liuku_summain(5, 11), liuku_kertoja(5, 11)),
    ("bfloat16 (e8, m8)", liuku_summain(8, 8), liuku_kertoja(8, 8)),
    ("binary32 (e8, m24)", liuku_summain(8, 24), liuku_kertoja(8, 24)),
]
print(f"{'muoto':19} {'summain':>8} {'kertoja':>8}")
for nimi, s, k in rivit:
    print(f"{nimi:19} {s:>8.0f} {k:>8.0f}")
# @loppu taulukko
