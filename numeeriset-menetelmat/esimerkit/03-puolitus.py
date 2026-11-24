"""Puolitushaku ja sen etukäteen tunnettu virheraja."""

import math
from collections.abc import Callable


# @alku puolitus
def puolitus(f: Callable[[float], float], a: float, b: float,
             tol: float) -> tuple[float, int]:
    """Juuri välillä [a, b], kun f(a) ja f(b) ovat erimerkkiset.

    Virhe on enintään (b - a) / 2^(k+1) k:n puolituksen jälkeen, joten
    kierrosten määrä tiedetään ennen laskua.
    """
    fa = f(a)
    if fa * f(b) > 0:
        raise ValueError("f(a) ja f(b) ovat samanmerkkiset")
    kierroksia = 0
    while (b - a) / 2 > tol:
        c = a + (b - a) / 2          # ei (a + b) / 2: ylivuoto ja pyöristys
        fc = f(c)
        if fc == 0:
            return c, kierroksia
        if (fc < 0) == (fa < 0):
            a, fa = c, fc
        else:
            b = c
        kierroksia += 1
    return a + (b - a) / 2, kierroksia
# @loppu puolitus


# @alku ajo
def f(x: float) -> float:
    return x**3 - 2 * x - 5          # Wallisin klassinen esimerkki


for tol in (1e-3, 1e-6, 1e-10):
    juuri, k = puolitus(f, 2.0, 3.0, tol)
    ennuste = math.ceil(math.log2(1.0 / tol)) - 1
    print(f"tol {tol:.0e}: juuri {juuri:.11f}, kierroksia {k} "
          f"(ennuste {ennuste})")
# @loppu ajo
