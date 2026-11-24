"""Eksponentiaalinen kasvu: kaksinkertaistumisaika ja jatkuva korko."""

import math

import sympy as sp

# @alku kasvu
# Palvelun käyttäjämäärä kasvaa 6 % kuukaudessa: N(t) = N0 * 1.06^t.
t = sp.symbols("t", positive=True)
N0 = 1000
N = N0 * sp.Rational(106, 100) ** t
tuplaus = sp.solve(sp.Eq(N, 2 * N0), t)[0]
print("solve antaa:", tuplaus)
siisti = sp.log(2) / sp.log(sp.Rational(106, 100))
print("sama kuin ln 2 / ln 1.06:", sp.simplify(tuplaus - siisti) == 0)
print("likiarvo:", round(float(tuplaus), 2), "kuukautta")
print("nyrkkisääntö 70/6 =", round(70 / 6, 2))
# @loppu kasvu

# @alku jatkuva
# Sama kasvu e-kantaisena: 1.06^t = e^(k t), k = ln 1.06.
k = math.log(1.06)
print(f"k = {k:.6f}, e^(12k) = {math.exp(12 * k):.6f}, "
      f"1.06^12 = {1.06**12:.6f}")
for vuodet in [1, 2, 5]:
    print(f"{vuodet} v: {N0 * 1.06 ** (12 * vuodet):10.0f} käyttäjää")
# @loppu jatkuva
