"""Ääriarvot: tölkin pienin pinta-ala ja suljetun välin ääriarvot."""

import sympy as sp

r, h, x = sp.symbols("r h x", positive=True)

# @alku tolkki
# Lieriö, tilavuus 0,5 l = 500 cm^3. Pinta-ala A = 2 pi r^2 + 2 pi r h.
# Tilavuusehdosta h = V/(pi r^2), jolloin A riippuu vain säteestä.
V = 500
korkeus = V / (sp.pi * r**2)
A = 2 * sp.pi * r**2 + 2 * sp.pi * r * korkeus
kriittiset = sp.solve(sp.diff(A, r), r)
r0 = kriittiset[0]
print("A'(r) = 0, kun r =", r0, "=", sp.N(r0, 4), "cm")
print("A''(r0) =", sp.N(sp.diff(A, r, 2).subs(r, r0), 4), "> 0: minimi")
print("korkeus/säde =", sp.simplify(korkeus.subs(r, r0) / r0))
print("pinta-ala", sp.N(A.subs(r, r0), 5), "cm^2")
# @loppu tolkki

# @alku suljettu
# Suljetulla välillä ääriarvo on kriittisessä pisteessä tai päätepisteessä.
f = x**3 - 6 * x**2 + 9 * x + 1
a, b = 0, 5
ehdokkaat = [p for p in sp.solve(sp.diff(f, x), x) if a <= p <= b]
ehdokkaat += [sp.Integer(a), sp.Integer(b)]
arvot = {p: f.subs(x, p) for p in ehdokkaat}
print("ehdokkaat:", arvot)
print("suurin", max(arvot.values()), "pienin", min(arvot.values()))
# @loppu suljettu
