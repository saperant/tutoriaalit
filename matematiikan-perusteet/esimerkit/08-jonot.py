"""Aritmeettinen ja geometrinen jono: rekursio ja suljettu muoto."""

import sympy as sp

n = sp.symbols("n", integer=True, positive=True)

# @alku aritmeettinen
# Palvelimen loki kasvaa 40 Mt päivässä, alussa 120 Mt.
a1, d = 120, 40
rekursio = [a1]
for _ in range(5):
    rekursio.append(rekursio[-1] + d)
suljettu = a1 + (n - 1) * d
print("rekursio:", rekursio)
print("suljettu:", [suljettu.subs(n, k) for k in range(1, 7)])
print("milloin yli 1000 Mt:", sp.ceiling(sp.solve(suljettu - 1000, n)[0]))
# @loppu aritmeettinen

# @alku geometrinen
# Puskuri kaksinkertaistuu, kun se täyttyy: 16, 32, 64, ...
b1, q = 16, 2
geometrinen = b1 * q ** (n - 1)
print("koot:", [geometrinen.subs(n, k) for k in range(1, 8)])
print("monesko koko riittää 10^6 alkiolle:",
      sp.ceiling(sp.solve(geometrinen - 10**6, n)[0]))
# @loppu geometrinen

# @alku rsolve
f = sp.Function("f")
print("rsolve:", sp.rsolve(f(n + 1) - 3 * f(n) - 2, f(n), {f(1): 1}))
# @loppu rsolve
