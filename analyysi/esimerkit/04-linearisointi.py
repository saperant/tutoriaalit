"""Linearisointi ja herkkyys: pieni muutos syötteessä, muutos tuloksessa."""

import sympy as sp

x, L, g = sp.symbols("x L g", positive=True)

# @alku lineaarinen
# Tangentti on funktion paras lineaarinen approksimaatio:
# f(a + dx) ~ f(a) + f'(a) dx.
f = sp.sqrt(x)
a = 100
lin = f.subs(x, a) + sp.diff(f, x).subs(x, a) * (x - a)
for arvo in (101, 110, 150):
    print(f"sqrt({arvo}) = {float(f.subs(x, arvo)):.5f}, "
          f"linearisointi {float(lin.subs(x, arvo)):.5f}")
# @loppu lineaarinen

# @alku heiluri
# Heilurin jaksonaika T = 2 pi sqrt(L/g). Suhteellinen herkkyys
# (dT/T)/(dL/L) = L/T * dT/dL kertoo, montako prosenttia T muuttuu,
# kun L muuttuu prosentin.
T = 2 * sp.pi * sp.sqrt(L / g)
herkkyys = sp.simplify(L / T * sp.diff(T, L))
print("herkkyys L:n suhteen:", herkkyys)
print("herkkyys g:n suhteen:", sp.simplify(g / T * sp.diff(T, g)))
# Varren pituuden 2 %:n mittausvirhe -> jaksonajan virhe noin 1 %.
T0 = T.subs({L: 1, g: sp.Float(9.81)})
T1 = T.subs({L: sp.Float(1.02), g: sp.Float(9.81)})
print(f"T: {float(T0):.4f} s -> {float(T1):.4f} s, "
      f"muutos {float((T1 - T0) / T0) * 100:.3f} %")
# @loppu heiluri
