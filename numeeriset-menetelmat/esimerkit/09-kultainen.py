"""Kultaisen leikkauksen haku yksiulotteiseen minimointiin."""

import math
from collections.abc import Callable

PHI = (math.sqrt(5) - 1) / 2         # ~0.618


# @alku kultainen
def kultainen(f: Callable[[float], float], a: float, b: float,
              tol: float) -> tuple[float, int]:
    """Minimi unimodaaliselle funktiolle välillä [a, b]. Väli lyhenee
    joka kierroksella kertoimella 0.618, ja kierroksella tarvitaan vain
    yksi uusi funktion arvo, koska toinen sisäpiste kierrätetään."""
    c, d = b - PHI * (b - a), a + PHI * (b - a)
    fc, fd = f(c), f(d)
    arvoja = 2
    while b - a > tol:
        if fc < fd:                   # minimi välillä [a, d]
            b, d, fd = d, c, fc
            c = b - PHI * (b - a)
            fc = f(c)
        else:                         # minimi välillä [c, b]
            a, c, fc = c, d, fd
            d = a + PHI * (b - a)
            fd = f(d)
        arvoja += 1
    return (a + b) / 2, arvoja
# @loppu kultainen


# @alku ajo
# Laatikon tilavuus, kun neliön (sivu 1) kulmista leikataan x:n kokoiset
# neliöt: V = x (1 - 2x)^2, maksimi kohdassa x = 1/6.
def miinus_tilavuus(x: float) -> float:
    return -x * (1 - 2 * x) ** 2


for tol in (1e-4, 1e-8):
    x, n = kultainen(miinus_tilavuus, 0.0, 0.5, tol)
    ennuste = math.ceil(math.log(tol / 0.5) / math.log(PHI)) + 2
    print(f"tol {tol:.0e}: x = {x:.8f}, arvoja {n} (ennuste {ennuste})")
print(f"tarkka 1/6 = {1 / 6:.8f}")
# @loppu ajo
