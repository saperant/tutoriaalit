"""Routhin–Hurwitzin kriteeri ja takaisinkytkennän vahvistus."""

import numpy as np
import sympy as sp


# @alku routh
def routh(kertoimet: list[sp.Expr]) -> list[list[sp.Expr]]:
    """Routhin taulukko polynomille (kertoimet korkeimmasta alkaen).

    Ensimmäisen sarakkeen merkinvaihtojen määrä on oikean puolitason
    juurten määrä. Erikoistapauksia (nolla ensimmäisessä sarakkeessa)
    ei käsitellä.
    """
    n = len(kertoimet)
    leveys = (n + 1) // 2
    rivit = [
        list(kertoimet[0::2])
        + [sp.Integer(0)] * (leveys - len(kertoimet[0::2])),
        list(kertoimet[1::2])
        + [sp.Integer(0)] * (leveys - len(kertoimet[1::2])),
    ]
    for _ in range(n - 2):
        a, b = rivit[-2], rivit[-1]
        uusi = [
            sp.simplify((b[0] * a[j + 1] - a[0] * b[j + 1]) / b[0])
            for j in range(leveys - 1)
        ] + [sp.Integer(0)]
        rivit.append(uusi)
    return rivit


# @loppu routh


# @alku vahvistus
# Prosessi G(s) = 1 / (s (s + 1) (s + 2)) ja P-säädin K
# takaisinkytkennässä.
# Suljetun silmukan karakteristinen polynomi: s^3 + 3 s^2 + 2 s + K.
K = sp.symbols("K", positive=True)
taulukko = routh([sp.Integer(1), sp.Integer(3), sp.Integer(2), K])
print("ensimmäinen sarake:", [r[0] for r in taulukko])
print("vakaa, kun", sp.solve([r[0] > 0 for r in taulukko], K))
for k in (2, 6, 8):
    juuret = np.roots([1, 3, 2, k])
    oikealla = sum(1 for z in juuret if z.real > 1e-9)
    suurin = max(z.real for z in juuret)
    print(
        f"K = {k}: suurin reaaliosa {round(suurin, 4) + 0.0:+.4f}, "
        f"juuria oikealla {oikealla}"
    )
# @loppu vahvistus
