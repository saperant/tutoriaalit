"""Suorat tasossa: yhtälöt, leikkauspiste ja pisteen etäisyys."""

import sympy as sp

x, y, t = sp.symbols("x y t", real=True)

# @alku suora
P, Q = sp.Matrix([1, 2]), sp.Matrix([5, 4])
suunta = Q - P
kulmakerroin = suunta[1] / suunta[0]
print("kulmakerroin:", kulmakerroin)
print("y = kx + b:", sp.expand(kulmakerroin * (x - P[0]) + P[1]))
normaali = sp.Matrix([-suunta[1], suunta[0]])
print("normaalimuoto:", sp.expand(normaali.dot(sp.Matrix([x, y]) - P)),
      "= 0")
print("parametrimuoto:", list(P + t * suunta))
# @loppu suora

# @alku leikkaus
suora1 = sp.Eq(y, x / 2 + sp.Rational(3, 2))
suora2 = sp.Eq(y, -2 * x + 9)
print("leikkauspiste:", sp.solve([suora1, suora2], [x, y]))
print("kohtisuorassa:", sp.Rational(1, 2) * (-2) == -1)
# @loppu leikkaus


# @alku etaisyys
def etaisyys(a: int, b: int, c: int, px: int, py: int) -> sp.Expr:
    """Pisteen (px, py) etäisyys suorasta ax + by + c = 0."""
    return sp.Abs(a * px + b * py + c) / sp.sqrt(a**2 + b**2)


d = etaisyys(-2, 4, -6, 4, 0)       # suora -2x + 4y - 6 = 0, piste (4, 0)
print("etäisyys:", d, "=", round(float(d), 4))
# @loppu etaisyys
