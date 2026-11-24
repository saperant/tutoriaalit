"""Määrittely- ja arvojoukko symbolisesti."""

import sympy as sp
from sympy.calculus.util import continuous_domain, function_range

x = sp.symbols("x", real=True)
R = sp.S.Reals

# @alku joukot
funktiot = {
    "sqrt(x - 1)": sp.sqrt(x - 1),
    "1/(x^2 - 4)": 1 / (x**2 - 4),
    "ln(3 - x)": sp.log(3 - x),
    "x^2 - 2x": x**2 - 2 * x,
}
for nimi, f in funktiot.items():
    maarittely = continuous_domain(f, x, R)
    arvot = function_range(f, x, maarittely)
    print(f"{nimi:12s} määrittely {maarittely}")
    print(f"{'':12s} arvot      {arvot}")
# @loppu joukot
