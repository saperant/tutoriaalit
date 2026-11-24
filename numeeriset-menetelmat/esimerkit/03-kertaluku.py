"""Suppenemiskertaluvun mittaaminen: kiintopiste, sekantti ja Newton.

Iteraatiot lasketaan 80 numeron tarkkuudella (decimal), jotta virheet
näkyvät monen kierroksen ajan ennen kuin pyöristys peittää ne.
"""

import math
from collections.abc import Callable
from decimal import Decimal, getcontext

getcontext().prec = 80
D = Decimal


def f(x: Decimal) -> Decimal:
    return x**3 - 2 * x - 5


def df(x: Decimal) -> Decimal:
    return 3 * x**2 - 2


# @alku menetelmat
def newton(x: Decimal, n: int) -> list[Decimal]:
    arvot = [x]
    for _ in range(n):
        x -= f(x) / df(x)
        arvot.append(x)
    return arvot


def sekantti(x0: Decimal, x1: Decimal, n: int) -> list[Decimal]:
    """Derivaatan tilalla kahden edellisen pisteen erotusosamäärä."""
    arvot = [x0, x1]
    for _ in range(n):
        f0, f1 = f(x0), f(x1)
        x0, x1 = x1, x1 - f1 * (x1 - x0) / (f1 - f0)
        arvot.append(x1)
    return arvot


def kiintopiste(x: Decimal, n: int) -> list[Decimal]:
    """x = (2x + 5)^(1/3); |g'(x*)| ~ 0.15, lineaarinen."""
    arvot = [x]
    for _ in range(n):
        x = (2 * x + 5) ** (D(1) / 3)
        arvot.append(x)
    return arvot
# @loppu menetelmat


JUURI = newton(D(2), 12)[-1]


# @alku kertaluku
def kertaluvut(arvot: list[Decimal]) -> list[float]:
    """p ~ log(e[k+1]/e[k]) / log(e[k]/e[k-1]) peräkkäisistä virheistä."""
    e = [float(abs(x - JUURI)) for x in arvot]
    e = [v for v in e if v > 1e-60]
    return [math.log(e[k + 1] / e[k]) / math.log(e[k] / e[k - 1])
            for k in range(1, len(e) - 1)]


tapaukset: list[tuple[str, Callable[[], list[Decimal]]]] = [
    ("kiintopiste", lambda: kiintopiste(D(2), 12)),
    ("sekantti", lambda: sekantti(D(2), D(3), 9)),
    ("Newton", lambda: newton(D(3), 7)),
]
for nimi, laske in tapaukset:
    p = kertaluvut(laske())
    print(f"{nimi:12s}", " ".join(f"{v:5.2f}" for v in p[-5:]))
print(f"kultainen leikkaus (1 + sqrt 5) / 2 = {(1 + math.sqrt(5)) / 2:.3f}")
# @loppu kertaluku


# @alku moninkertainen
# Kaksinkertaisella juurella f'(x*) = 0, ja Newton hidastuu
# lineaariseksi (suhde 1/2). Kertoimella m = 2 neliöllisyys palaa.
def g(x: float) -> float:
    return (x - 1) ** 2 * (x + 2)


def dg(x: float) -> float:
    return 2 * (x - 1) * (x + 2) + (x - 1) ** 2


for m in (1, 2):
    x, virheet = 2.0, []
    for _ in range(6):
        if g(x) == 0:
            break
        x -= m * g(x) / dg(x)
        virheet.append(abs(x - 1))
    print(f"m={m}: virheet", " ".join(f"{v:.1e}" for v in virheet))
# @loppu moninkertainen
