"""Nollakohta puolitushaulla ja sen virheraja."""

import math
from collections.abc import Callable

import sympy as sp


# @alku puolitus
def puolitus(f: Callable[[float], float], a: float, b: float,
             toleranssi: float) -> tuple[float, int]:
    """Etsii f:n nollakohdan välillä [a, b], kun f(a) ja f(b) ovat
    erimerkkiset. Palauttaa likiarvon ja kierrosten määrän."""
    fa = f(a)
    if fa * f(b) > 0:
        raise ValueError("f(a) ja f(b) ovat samanmerkkiset")
    kierroksia = 0
    while b - a > 2 * toleranssi:
        c = (a + b) / 2
        fc = f(c)
        if fa * fc <= 0:
            b = c
        else:
            a, fa = c, fc
        kierroksia += 1
    return (a + b) / 2, kierroksia
# @loppu puolitus


# @alku kaytto
def f(x: float) -> float:
    return x**3 - x - 2


juuri, n = puolitus(f, 1.0, 2.0, 1e-9)
print(f"juuri {juuri:.9f}, kierroksia {n}")
print("ennuste: ceil(log2(1 / 2e-9)) =", math.ceil(math.log2(1 / 2e-9)))
x = sp.symbols("x")
print("nsolve:", sp.N(sp.nsolve(x**3 - x - 2, x, 1.5), 10))
# @loppu kaytto

# @alku virhe
try:
    puolitus(f, 2.0, 3.0, 1e-6)
except ValueError as virhe:
    print("virhe:", virhe)
# @loppu virhe
