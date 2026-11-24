"""Konvoluutio: tulo s-tasossa on konvoluutio aikatasossa."""

import sympy as sp

t, tau = sp.symbols("t tau", positive=True)
s = sp.symbols("s")

# @alku konvoluutio
# Järjestelmän impulssivaste h(t) = exp(-t) ja tulo u(t) = sin(t).
# Lähtö on konvoluutio (h * u)(t) = int_0^t h(t - tau) u(tau) dtau.
h = sp.exp(-t)
u = sp.sin(t)
aikataso = sp.integrate(h.subs(t, t - tau) * u.subs(t, tau), (tau, 0, t))
print("konvoluutio:", sp.simplify(aikataso))
H = sp.laplace_transform(h, t, s, noconds=True)
U = sp.laplace_transform(u, t, s, noconds=True)
staso = sp.inverse_laplace_transform(H * U, s, t)
print("L^-1{H U}:  ", sp.simplify(staso))
print("sama:", sp.simplify(aikataso - staso) == 0)
# @loppu konvoluutio
