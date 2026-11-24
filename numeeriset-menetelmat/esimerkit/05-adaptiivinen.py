"""Adaptiivinen Simpson: pisteitä vain sinne, missä funktio vaihtelee."""

import math
from collections.abc import Callable

from scipy import integrate

Funktio = Callable[[float], float]


# @alku adaptiivinen
def adaptiivinen(f: Funktio, a: float, b: float, tol: float) -> tuple[
        float, int]:
    """Palauttaa integraalin ja funktion arvojen määrän."""
    laskuri = 0

    def arvo(x: float) -> float:
        nonlocal laskuri
        laskuri += 1
        return f(x)

    def simpson(a: float, fa: float, b: float, fb: float
                ) -> tuple[float, float, float]:
        m = (a + b) / 2
        fm = arvo(m)
        return m, fm, (b - a) / 6 * (fa + 4 * fm + fb)

    def osa(a: float, fa: float, b: float, fb: float, m: float, fm: float,
            koko: float, tol: float) -> float:
        lm, flm, vasen = simpson(a, fa, m, fm)
        rm, frm, oikea = simpson(m, fm, b, fb)
        ero = vasen + oikea - koko
        if abs(ero) <= 15 * tol:        # virhearvio Richardsonin tapaan
            return vasen + oikea + ero / 15
        return (osa(a, fa, m, fm, lm, flm, vasen, tol / 2)
                + osa(m, fm, b, fb, rm, frm, oikea, tol / 2))

    fa, fb = arvo(a), arvo(b)
    m, fm, koko = simpson(a, fa, b, fb)
    return osa(a, fa, b, fb, m, fm, koko, tol), laskuri
# @loppu adaptiivinen


# @alku vertailu
# Kapea huippu (leveys ~0.001) kohdassa x0 ja muuten loiva funktio.
X0, C = 0.31415, 1e-6


def f(x: float) -> float:
    return 1 / (C + (x - X0) ** 2) + x


a = math.sqrt(C)
tarkka = (math.atan((1 - X0) / a) + math.atan(X0 / a)) / a + 0.5
arvo, n = adaptiivinen(f, 0.0, 1.0, 1e-6)
print(f"adaptiivinen Simpson: suhteellinen virhe "
      f"{abs(arvo - tarkka) / tarkka:.0e}, arvoja {n}")
m = n - n % 2                         # sama määrä arvoja tasavälisesti
h = 1.0 / m
tasa = h / 3 * (f(0) + f(1) + sum(
    (4 if k % 2 else 2) * f(k * h) for k in range(1, m)))
print(f"tasavälinen Simpson:  suhteellinen virhe "
      f"{abs(tasa - tarkka) / tarkka:.0e}, arvoja {m + 1}")
q, arvio, tiedot = integrate.quad(f, 0, 1, full_output=True,
                                  epsrel=1e-12, limit=200)[:3]
virhe = abs(q - tarkka) / tarkka
print(f"quad (Gauss-Kronrod): suhteellinen virhe "
      f"{'< 1e-13' if virhe < 1e-13 else f'{virhe:.0e}'}, "
      f"arvoja {tiedot['neval']}")
# @loppu vertailu
