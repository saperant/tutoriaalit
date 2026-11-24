"""Taylorin polynomit, jäännöstermi ja insinöörin approksimaatiot."""

import math

import sympy as sp

x = sp.symbols("x", real=True)

# @alku sarja
print("sin x =", sp.series(sp.sin(x), x, 0, 8))
print("e^x   =", sp.series(sp.exp(x), x, 0, 5))
print("ln(1+x) =", sp.series(sp.log(1 + x), x, 0, 5))
print("1/(1-x) =", sp.series(1 / (1 - x), x, 0, 5))
# @loppu sarja


# @alku taylor
def taylor(f: sp.Expr, a: int, aste: int) -> sp.Expr:
    """Taylorin polynomi kehityskohdassa a: sum f^(k)(a)/k! (x-a)^k."""
    return sp.Add(*[sp.diff(f, x, k).subs(x, a) / sp.factorial(k)
                    * (x - a) ** k for k in range(aste + 1)])


p5 = taylor(sp.sin(x), 0, 5)
print("P5(x) =", p5)
# Jäännöstermi: |sin x - P5(x)| <= |x|^7/7!, koska |sin^(7)| <= 1.
for arvo in (0.5, 1.0, 2.0, 3.0):
    virhe = abs(math.sin(arvo) - float(p5.subs(x, arvo)))
    raja = arvo**7 / math.factorial(7)
    print(f"x={arvo}: virhe {virhe:.2e}, yläraja {raja:.2e}")
# @loppu taylor

# @alku pieni
# Pienen kulman approksimaatiot: sin x ~ x, cos x ~ 1 - x^2/2.
for aste in (1, 5, 10, 20):
    r = math.radians(aste)
    sin_virhe = (r - math.sin(r)) / math.sin(r)
    cos_virhe = abs(1 - r * r / 2 - math.cos(r)) / math.cos(r)
    print(f"kulma {aste:2d} astetta: sin-virhe {sin_virhe:.2%},"
          f" cos-virhe {cos_virhe:.3%}")
# @loppu pieni
