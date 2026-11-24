"""Newtonin menetelmä: neliöllinen suppeneminen ja epäonnistumiset."""

import math
from collections.abc import Callable

from scipy import optimize


# @alku newton
def newton(f: Callable[[float], float], df: Callable[[float], float],
           x: float, kierroksia: int) -> list[float]:
    """Newtonin iteraatio x <- x - f(x)/f'(x). Palauttaa kaikki arvot."""
    arvot = [x]
    for _ in range(kierroksia):
        derivaatta = df(x)
        if derivaatta == 0:
            raise ZeroDivisionError(f"f'(x) = 0 kohdassa x = {x}")
        x = x - f(x) / derivaatta
        arvot.append(x)
    return arvot
# @loppu newton


# @alku sqrt2
# sqrt(2) yhtälön x^2 - 2 = 0 juurena: oikeiden numeroiden määrä
# kaksinkertaistuu joka kierroksella.
for x in newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0, 5):
    virhe = abs(x - math.sqrt(2))
    print(f"{x:.16f}  virhe {virhe:.1e}")
# @loppu sqrt2

# @alku epaonnistuu
# 1) Kuutiojuurella x^(1/3) askel on -2x: iteraatio karkaa.
def kuutio(x: float) -> float:
    return math.copysign(abs(x) ** (1 / 3), x)


def dkuutio(x: float) -> float:
    return float(abs(x) ** (-2 / 3)) / 3


print("x^(1/3):", [f"{v:g}" for v in newton(kuutio, dkuutio, 0.1, 5)])
# 2) Funktiolla x^3 - 2x + 2 alkuarvo 0 jää kiertämään kehää 0, 1, 0, ...
print("kehä:", newton(lambda x: x**3 - 2 * x + 2,
                      lambda x: 3 * x**2 - 2, 0.0, 4))
# 3) Vaakasuora tangentti: f'(x) = 0.
try:
    newton(lambda x: x * x - 2, lambda x: 2 * x, 0.0, 1)
except ZeroDivisionError as e:
    print("virhe:", e)
# @loppu epaonnistuu

# @alku scipy
# Kirjastoversio: brentq yhdistää puolitushaun varmuuden ja nopeamman
# interpoloinnin; se tarvitsee välin, jolla merkki vaihtuu.
juuri = optimize.brentq(lambda x: x**3 - 2 * x + 2, -3.0, 0.0)
print(f"brentq: {juuri:.12f}")
# @loppu scipy
