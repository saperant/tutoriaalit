"""Eulerin menetelmä ja klassinen Runge–Kutta (RK4) omina toteutuksina."""

import math
from collections.abc import Callable

Funktio = Callable[[float, float], float]


# @alku menetelmat
def euler(f: Funktio, t: float, y: float, h: float, n: int) -> float:
    """Eulerin menetelmä: kuljetaan tangentin suuntaan askel kerrallaan."""
    for _ in range(n):
        y += h * f(t, y)
        t += h
    return y


def rk4(f: Funktio, t: float, y: float, h: float, n: int) -> float:
    """RK4: neljän kulmakertoimen painotettu keskiarvo askeleella."""
    for _ in range(n):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h / 2 * k1)
        k3 = f(t + h / 2, y + h / 2 * k2)
        k4 = f(t + h, y + h * k3)
        y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += h
    return y


# @loppu menetelmat


# @alku vertailu
# y' = -2 t y, y(0) = 1, tarkka ratkaisu exp(-t^2). Lasketaan y(1).
def f(t: float, y: float) -> float:
    return -2 * t * y


tarkka = math.exp(-1)
print("    n   h       Euler-virhe   RK4-virhe")
for n in (10, 20, 40, 80):
    h = 1 / n
    ve = abs(euler(f, 0.0, 1.0, h, n) - tarkka)
    vr = abs(rk4(f, 0.0, 1.0, h, n) - tarkka)
    print(f"{n:5d}  {h:.4f}  {ve:.3e}     {vr:.3e}")
# @loppu vertailu
