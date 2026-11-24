"""Korkoa korolle ja annuiteettilaina: kaava ja simulaatio."""

from fractions import Fraction

import sympy as sp

# @alku korko
# 5000 euroa, 3 % vuosikorko, 10 vuotta: K = K0 (1 + p)^n.
K0, p, vuodet = 5000, Fraction(3, 100), 10
kaava = K0 * (1 + p) ** vuodet
saldo = Fraction(K0)
for _ in range(vuodet):
    saldo += saldo * p
print(f"kaava {float(kaava):.2f}, simulaatio {float(saldo):.2f}, "
      f"sama tarkasti: {kaava == saldo}")
# @loppu korko

# @alku annuiteetti
# Laina L, kuukausikorko i, n erää. Viimeisen erän jälkeen saldo on 0:
# L (1 + i)^n = A (1 + (1 + i) + ... + (1 + i)^(n - 1)).
L, i, n, A = sp.symbols("L i n A", positive=True)
k = sp.symbols("k", integer=True)
summa = sp.summation((1 + i) ** k, (k, 0, n - 1))
era = sp.solve(sp.Eq(L * (1 + i) ** n, A * summa), A)[0]
print("erä A =", sp.simplify(era))
arvot = {L: 150_000, i: sp.Rational(4, 100) / 12, n: 25 * 12}
kuukausiera = float(era.subs(arvot))
print(f"150 000 eur, 4 %, 25 v: {kuukausiera:.2f} eur/kk, "
      f"korkoja yhteensä {kuukausiera * 300 - 150_000:.0f} eur")
# @loppu annuiteetti

# @alku simulaatio
velka = 150_000.0
for _ in range(300):
    velka = velka * (1 + 0.04 / 12) - kuukausiera
print(f"velka 300 erän jälkeen: {abs(velka):.6f} eur")
# @loppu simulaatio
