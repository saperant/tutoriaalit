"""Trigonometriset yhtälöt: yleinen ratkaisu ja ratkaisut välillä."""

import sympy as sp

x = sp.symbols("x", real=True)

# @alku yleinen
yleinen = sp.solveset(sp.sin(x) - sp.Rational(1, 2), x, sp.S.Reals)
print("sin x = 1/2, yhdiste joukoista:")
for osa in yleinen.args:
    print("  ", osa)
# @loppu yleinen

# @alku valilla
vali = sp.Interval(0, 4 * sp.pi)
print("välillä [0, 4 pi]:",
      sp.solveset(sp.sin(x) - sp.Rational(1, 2), x, vali))
print("cos 2x = cos x, [0, 2 pi):",
      sp.solveset(sp.cos(2 * x) - sp.cos(x), x,
                  sp.Interval.Ropen(0, 2 * sp.pi)))
# @loppu valilla

# @alku tarkistus
for juuri in sp.solveset(sp.sin(x) - sp.Rational(1, 2), x, vali):
    print(f"sin({juuri}) = {sp.sin(juuri)}")
# @loppu tarkistus
