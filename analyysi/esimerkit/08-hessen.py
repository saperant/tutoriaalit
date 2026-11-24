"""Kriittisten pisteiden luokittelu Hessen matriisilla ja Jacobin matriisi."""

import sympy as sp

x, y, r, th = sp.symbols("x y r theta", real=True)

# @alku luokittelu
f = x**3 - 3 * x + y**2
kriittiset = sp.solve([sp.diff(f, x), sp.diff(f, y)], [x, y], dict=True)
H = sp.hessian(f, (x, y))
print("Hessen matriisi:", H.tolist())
for p in kriittiset:
    Hp = H.subs(p)
    ominais = list(Hp.eigenvals())
    if all(e > 0 for e in ominais):
        laji = "minimi"
    elif all(e < 0 for e in ominais):
        laji = "maksimi"
    else:
        laji = "satulapiste"
    print(f"  ({p[x]}, {p[y]}): ominaisarvot {ominais} -> {laji}")
# @loppu luokittelu

# @alku jacobi
# Napakoordinaatit x = r cos t, y = r sin t. Jacobin matriisi kertoo,
# miten pieni muutos (dr, dt) kuvautuu muutokseksi (dx, dy).
X = sp.Matrix([r * sp.cos(th), r * sp.sin(th)])
J = X.jacobian([r, th])
print("J =", J.tolist())
print("det J =", sp.simplify(J.det()))
# @loppu jacobi
