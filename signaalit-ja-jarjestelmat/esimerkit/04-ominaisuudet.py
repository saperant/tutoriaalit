"""Järjestelmän ominaisuuksien numeerinen testaus koesignaaleilla."""

from collections.abc import Callable

import numpy as np
import numpy.typing as npt

Jono = npt.NDArray[np.float64]
Jarjestelma = Callable[[Jono], Jono]


# @alku jarjestelmat
def keskiarvo3(x: Jono) -> Jono:              # y[n] = (x[n]+x[n-1]+x[n-2])/3
    return np.convolve(x, np.ones(3) / 3)[:len(x)]


def nelio(x: Jono) -> Jono:                   # y[n] = x[n]^2
    return x**2


def aikapaino(x: Jono) -> Jono:               # y[n] = n x[n]
    return np.arange(len(x)) * x


def edistys(x: Jono) -> Jono:                 # y[n] = x[n+1]
    return np.append(x[1:], 0.0)


def summain(x: Jono) -> Jono:                 # y[n] = sum_{k<=n} x[k]
    return np.cumsum(x)


def poikkeama(x: Jono) -> Jono:               # y[n] = 2 x[n] + 1
    return 2 * x + 1
# @loppu jarjestelmat


# @alku testit
rng = np.random.default_rng(7)
N = 64


def lineaarinen(T: Jarjestelma) -> bool:
    x1, x2 = rng.normal(size=N), rng.normal(size=N)
    a, b = rng.normal(), rng.normal()
    return bool(np.allclose(T(a * x1 + b * x2), a * T(x1) + b * T(x2)))


def aikainvariantti(T: Jarjestelma, viive: int = 5) -> bool:
    x = np.concatenate([rng.normal(size=N - 10), np.zeros(10)])
    siirretty = np.concatenate([np.zeros(viive), x[:-viive]])
    # Siirretyn syötteen vasteen on oltava siirretty vaste.
    return bool(np.allclose(T(siirretty)[viive:], T(x)[:-viive]))


def kausaalinen(T: Jarjestelma, n0: int = 30) -> bool:
    """Muutos hetkestä n0 alkaen ei saa näkyä ennen hetkeä n0."""
    x1 = rng.normal(size=N)
    x2 = x1.copy()
    x2[n0:] += rng.normal(size=N - n0)
    return bool(np.allclose(T(x1)[:n0], T(x2)[:n0]))
# @loppu testit


# @alku taulukko
print(f"{'järjestelmä':<11} {'lineaar.':>8} {'aikainv.':>8}"
      f" {'kausaal.':>8}")
for T in (keskiarvo3, nelio, aikapaino, edistys, summain, poikkeama):
    tulos = (lineaarinen(T), aikainvariantti(T), kausaalinen(T))
    print(f"{T.__name__:<11}", " ".join(f"{str(v):>8}" for v in tulos))
# @loppu taulukko
