"""Nolla-avaruus: reaktioyhtälön tasapainotus lineaarialgebralla."""

import math
from fractions import Fraction


def porrasmuoto(m: list[list[Fraction]]) -> tuple[list[list[Fraction]],
                                                   list[int]]:
    """Redusoitu porrasmuoto tarkoilla murtoluvuilla ja tukisarakkeet."""
    m = [rivi[:] for rivi in m]
    tuet: list[int] = []
    r = 0
    for s in range(len(m[0])):
        p = next((i for i in range(r, len(m)) if m[i][s] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        m[r] = [x / m[r][s] for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][s] != 0:
                k = m[i][s]
                m[i] = [x - k * y for x, y in zip(m[i], m[r], strict=True)]
        tuet.append(s)
        r += 1
    return m, tuet


# @alku nolla-avaruus
def nolla_avaruus(a: list[list[int]]) -> list[list[Fraction]]:
    """Nolla-avaruuden kanta: kukin vapaa muuttuja = 1, muut vapaat = 0,
    ja tukimuuttujat porrasmuodosta."""
    m, tuet = porrasmuoto([[Fraction(x) for x in rivi] for rivi in a])
    n = len(a[0])
    kanta = []
    for vapaa in (s for s in range(n) if s not in tuet):
        x = [Fraction(0)] * n
        x[vapaa] = Fraction(1)
        for rivi, tuki in zip(m, tuet, strict=False):
            x[tuki] = -rivi[vapaa]
        kanta.append(x)
    return kanta
# @loppu nolla-avaruus


# @alku reaktio
# a CH4 + b O2 -> c CO2 + d H2O. Jokaisen alkuaineen atomimäärä
# säilyy: yksi yhtälö alkuainetta kohti, tuotteet negatiivisina.
#          CH4  O2  CO2  H2O
alkuaineet = {"C": [1, 0, -1, 0],
              "H": [4, 0, 0, -2],
              "O": [0, 2, -2, -1]}
kanta = nolla_avaruus(list(alkuaineet.values()))
print("nolla-avaruuden ulottuvuus:", len(kanta))
x = kanta[0]
nimittaja = math.lcm(*(k.denominator for k in x))
kertoimet = [int(k * nimittaja) for k in x]
print("kertoimet:", kertoimet)
a, b, c, d = kertoimet
print(f"{a} CH4 + {b} O2 -> {c} CO2 + {d} H2O")
# @loppu reaktio
