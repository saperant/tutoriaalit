"""Toisen asteen yhtälö: ratkaisukaava, diskriminantti ja kumoutuminen."""

import math

import sympy as sp

# @alku kaava
a, b, c, x = sp.symbols("a b c x")
ratkaisut = sp.solve(a * x**2 + b * x + c, x)
for juuri in ratkaisut:
    print("x =", juuri)
D = b**2 - 4 * a * c
for kertoimet in [(1, -5, 6), (1, 2, 1), (1, 0, 1)]:
    arvot = dict(zip((a, b, c), kertoimet, strict=True))
    print(kertoimet, "D =", D.subs(arvot), "juuret:",
          sp.solve(sp.Poly([*kertoimet], x).as_expr(), x))
# @loppu kaava


# @alku kumoutuminen
def naiivi(a: float, b: float, c: float) -> tuple[float, float]:
    d = math.sqrt(b * b - 4 * a * c)
    return (-b + d) / (2 * a), (-b - d) / (2 * a)


def vakaa(a: float, b: float, c: float) -> tuple[float, float]:
    """Iso juuri ilman kumoutumista, pieni Vietan kaavasta x1*x2 = c/a."""
    d = math.sqrt(b * b - 4 * a * c)
    q = -(b + math.copysign(d, b)) / 2
    return q / a, c / q


# x^2 - 1e8 x + 1 = 0: juuret noin 1e8 ja 1e-8
print("naiivi:", naiivi(1.0, -1e8, 1.0))
print("vakaa: ", vakaa(1.0, -1e8, 1.0))
tarkka = sp.solve(x**2 - 10**8 * x + 1, x)
print("tarkka pieni juuri:", sp.N(min(tarkka), 10))
# @loppu kumoutuminen
