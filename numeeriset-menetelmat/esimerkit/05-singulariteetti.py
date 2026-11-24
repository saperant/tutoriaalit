"""Singulaarinen integrandi: 1/sqrt(x) välillä [0, 1], tarkka arvo 2."""

import math
from collections.abc import Callable

from scipy import integrate


# @alku keskipiste
def keskipiste(f: Callable[[float], float], n: int) -> float:
    """Keskipistesääntö ei tarvitse arvoa päätepisteessä x = 0."""
    h = 1.0 / n
    return h * sum(f((k + 0.5) * h) for k in range(n))


def f(x: float) -> float:
    return 1 / math.sqrt(x)


for n in (10, 100, 1000, 10000):
    print(f"keskipiste n={n:5d}: virhe {abs(keskipiste(f, n) - 2):.1e}")
# @loppu keskipiste

# @alku sijoitus
# Sijoitus x = t^2, dx = 2t dt: integrandi 2t / t = 2 on sileä.
def g(t: float) -> float:
    return 2.0


print(f"sijoituksen jälkeen n=10: virhe {abs(keskipiste(g, 10) - 2):.1e}")
# @loppu sijoitus

# @alku quad
q, arvio = integrate.quad(f, 0, 1)
print(f"quad: {q:.12f}, virhearvio < 1e-12: {arvio < 1e-12}")
# Painofunktio: quad integroi (x - 0)^(-1/2) * 1 erikoissäännöllä.
q2, _ = integrate.quad(lambda x: 1.0, 0, 1, weight="alg",
                       wvar=(-0.5, 0.0))
print(f"quad, weight='alg': {q2:.12f}")
# @loppu quad
