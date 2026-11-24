"""Trigonometristen kaavojen tarkistus symbolisesti ja numeerisesti."""

import math

import sympy as sp

x, y = sp.symbols("x y", real=True)

# @alku kaavat
kaavat = {
    "sin(2x) = 2 sin x cos x": (sp.sin(2 * x), 2 * sp.sin(x) * sp.cos(x)),
    "cos(2x) = 1 - 2 sin^2 x": (sp.cos(2 * x), 1 - 2 * sp.sin(x) ** 2),
    "sin(x+y) = sin x cos y + cos x sin y": (
        sp.sin(x + y), sp.sin(x) * sp.cos(y) + sp.cos(x) * sp.sin(y)),
    "tan(2x) = 2 tan x": (sp.tan(2 * x), 2 * sp.tan(x)),
}
for nimi, (vasen, oikea) in kaavat.items():
    ero = sp.simplify(sp.expand_trig(vasen - oikea))
    print(f"{nimi:38s} {'pätee' if ero == 0 else 'EI päde'}")
# @loppu kaavat


# @alku numeerinen
def poikkeama(vasen: sp.Expr, oikea: sp.Expr) -> float:
    """Suurin ero kymmenessä testipisteessä (pistokoe, ei todistus)."""
    f = sp.lambdify(x, vasen - oikea, modules="math")
    return float(max(abs(f(0.1 + 0.37 * k)) for k in range(10)))


vasen, oikea = kaavat["tan(2x) = 2 tan x"]
print(f"tan-kaavan poikkeama: {poikkeama(vasen, oikea):.1f}")
vasen, oikea = kaavat["cos(2x) = 1 - 2 sin^2 x"]
print("cos-kaavan poikkeama alle 1e-12:",
      poikkeama(vasen, oikea) < 1e-12)
print("tarkistus, pi/7:", math.isclose(math.cos(2 * math.pi / 7),
                                       1 - 2 * math.sin(math.pi / 7) ** 2))
# @loppu numeerinen
