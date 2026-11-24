"""Summausjärjestys, sum() ja math.fsum."""

import math


def naiivi(arvot: list[float]) -> float:
    """Summa vasemmalta oikealle, kuten C:n silmukka."""
    s = 0.0
    for x in arvot:
        s += x
    return s


# @alku jarjestys
arvot = [1e16] + [1.0] * 1000 + [-1e16]   # tilisaldon muutokset
print(naiivi(arvot), naiivi(sorted(arvot, key=abs)))
print(sum(arvot), math.fsum(arvot))     # sum kompensoi (Python 3.12+)
print(naiivi([0.1] * 10), sum([0.1] * 10))
# Yhteenlasku ei ole liitännäinen:
print((0.1 + 0.2) + 0.3, 0.1 + (0.2 + 0.3))
# @loppu jarjestys
