"""Summat symbolisesti: aritmeettinen, geometrinen ja harmoninen."""

import math

import sympy as sp

k, n = sp.symbols("k n", integer=True, positive=True)
q = sp.symbols("q", positive=True)

# @alku summat
print("1 + 2 + ... + n =", sp.factor(sp.summation(k, (k, 1, n))))
print("1^2 + ... + n^2 =", sp.factor(sp.summation(k**2, (k, 1, n))))
geom = sp.summation(q ** (k - 1), (k, 1, n))
print("1 + q + ... + q^(n-1) =", sp.simplify(geom))
print("äärettömästi, q = 1/2:",
      sp.summation(sp.Rational(1, 2) ** k, (k, 0, sp.oo)))
# @loppu summat

# @alku tyomaara
# Sisäkkäiset silmukat: for i < n: for j < i  ->  0 + 1 + ... + (n - 1).
vertailuja = sp.summation(k - 1, (k, 1, n))
print("vertailuja:", sp.factor(vertailuja), " n = 1000:",
      vertailuja.subs(n, 1000))
laskettu = sum(1 for i in range(1000) for _ in range(i))
print("silmukka laskee:", laskettu)
# @loppu tyomaara

# @alku harmoninen
# Harmoninen summa kasvaa kuten ln n: hajaantuu, mutta hitaasti.
for m in [10, 1000, 10**6]:
    h = math.fsum(1 / j for j in range(1, m + 1))
    print(f"H({m}) = {h:.6f}, ln n + 0.5772 = {math.log(m) + 0.5772:.6f}")
# @loppu harmoninen
