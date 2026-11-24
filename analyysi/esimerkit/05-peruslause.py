"""Analyysin peruslause: integraali lasketaan integraalifunktiolla."""

import sympy as sp

x, t = sp.symbols("x t", real=True)

# @alku peruslause
f = sp.sin(x)
F = sp.integrate(f, x)                  # integraalifunktio (ilman vakiota)
print("F(x) =", F, "; F'(x) =", sp.diff(F, x))
print("int_0^pi sin x dx =", F.subs(x, sp.pi) - F.subs(x, 0),
      "=", sp.integrate(f, (x, 0, sp.pi)))
# @loppu peruslause

# @alku ylaraja
# Peruslauseen toinen puoli: G(x) = int_0^x f(t) dt => G'(x) = f(x).
G = sp.Integral(sp.exp(-(t**2)), (t, 0, x))
print("G'(x) =", sp.diff(G, x))
print("G(x) =", G.doit(), "(virhefunktio, ei alkeisfunktiona)")
# @loppu ylaraja
