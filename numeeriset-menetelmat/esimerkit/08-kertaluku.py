"""ODE-ratkaisijoiden kertaluvut: Euler, Heun ja RK4."""

import math
from collections.abc import Callable

Derivaatta = Callable[[float, float], float]
Askel = Callable[[Derivaatta, float, float, float], float]


# @alku askeleet
def euler(f: Derivaatta, t: float, y: float, h: float) -> float:
    return y + h * f(t, y)


def heun(f: Derivaatta, t: float, y: float, h: float) -> float:
    """Eulerin ennuste ja puolisuunnikkaan korjaus: kertaluku 2."""
    k1 = f(t, y)
    k2 = f(t + h, y + h * k1)
    return y + h * (k1 + k2) / 2


def rk4(f: Derivaatta, t: float, y: float, h: float) -> float:
    """Klassinen Rungen-Kuttan menetelmä: neljä arvoa, kertaluku 4."""
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
# @loppu askeleet


# @alku ratkaise
def ratkaise(askel: Askel, f: Derivaatta, y0: float, T: float,
             n: int) -> float:
    h, t, y = T / n, 0.0, y0
    for _ in range(n):
        y = askel(f, t, y, h)
        t += h
    return y
# @loppu ratkaise


# @alku mittaus
# y' = -2 t y, y(0) = 1: tarkka ratkaisu y(t) = exp(-t^2).
def f(t: float, y: float) -> float:
    return -2 * t * y


tarkka = math.exp(-4.0)                    # y(2)
print("   n   Euler            Heun             RK4")
edelliset: list[float] = []
for n in (20, 40, 80, 160):
    virheet = [abs(ratkaise(a, f, 1.0, 2.0, n) - tarkka)
               for a in (euler, heun, rk4)]
    sarakkeet = [f"{v:.1e}" + ("" if not edelliset else
                                f" (x{edelliset[i] / v:4.1f})")
                 for i, v in enumerate(virheet)]
    print(f"{n:4d}   " + "  ".join(f"{s:15s}" for s in sarakkeet).rstrip())
    edelliset = virheet
# @loppu mittaus
