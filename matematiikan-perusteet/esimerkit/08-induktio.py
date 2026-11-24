"""Induktiotodistuksen vaiheiden tarkistus SymPyllä."""

import sympy as sp

n = sp.symbols("n", integer=True, positive=True)

# @alku induktio
# Väite: 1^3 + 2^3 + ... + n^3 = (n (n + 1) / 2)^2 kaikilla n >= 1.
F = (n * (n + 1) / 2) ** 2
perusaskel = F.subs(n, 1) == 1**3
# Induktioaskel: oletetaan S(n) = F(n); silloin S(n + 1) = F(n) + (n+1)^3.
askel = sp.expand(F + (n + 1) ** 3 - F.subs(n, n + 1)) == 0
print("perusaskel n = 1:", perusaskel)
print("induktioaskel n -> n + 1:", askel)
# @loppu induktio

# @alku vaara
# Väite "n^2 + n + 41 on alkuluku kaikilla n" pätee pitkään ...
kaava = n**2 + n + 41
ensimmainen = next(k for k in range(1, 100)
                   if not sp.isprime(kaava.subs(n, k)))
print("ensimmäinen vastaesimerkki: n =", ensimmainen,
      " arvo", kaava.subs(n, ensimmainen), "=",
      sp.factorint(kaava.subs(n, ensimmainen)))
# @loppu vaara

# @alku epayhtalo
# Väite: 2^n > n^2, kun n >= 5. Askel: 2^(n+1) = 2 * 2^n > 2 n^2,
# ja 2 n^2 >= (n + 1)^2, kun n^2 - 2n - 1 >= 0 eli n >= 3.
x = sp.symbols("x", real=True)
print("2n^2 >= (n+1)^2, kun:",
      sp.solveset(2 * x**2 - (x + 1) ** 2 >= 0, x, sp.Interval(0, sp.oo)))
print("perusaskel 2^5 > 5^2:", 2**5 > 5**2)
# @loppu epayhtalo
