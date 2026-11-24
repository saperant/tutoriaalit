"""Osittaisderivaatat, gradientti ja suunnattu derivaatta."""

import sympy as sp

x, y = sp.symbols("x y", real=True)

# @alku osittais
# Mäen korkeus (m) paikan (x, y) (km) funktiona.
h = 300 - 20 * x**2 - 40 * y**2 + 10 * x * y
hx, hy = sp.diff(h, x), sp.diff(h, y)
print("dh/dx =", hx, "; dh/dy =", hy)
# Sekaderivaatat ovat samat (Schwarzin lause).
print("h_xy =", sp.diff(h, x, y), "; h_yx =", sp.diff(h, y, x))
# @loppu osittais

# @alku gradientti
grad = sp.Matrix([hx, hy])
P = {x: 1, y: 1}
gP = grad.subs(P)
print("grad h(1, 1) =", list(gP), "; jyrkkyys", gP.norm(), "=",
      sp.N(gP.norm(), 4), "m/km")
# Suunnattu derivaatta yksikkövektorin u suuntaan: grad . u.
for nimi, u in (("itään", (1, 0)), ("koilliseen", (1, 1)),
                ("gradientin suuntaan", tuple(gP))):
    uv = sp.Matrix(u) / sp.Matrix(u).norm()
    print(f"  {nimi}: {sp.N(gP.dot(uv), 4)} m/km")
# @loppu gradientti

# @alku tasa-arvo
# Gradientti on kohtisuorassa tasa-arvokäyrää vastaan: käyrän tangentin
# suunta (-h_y, h_x) on gradienttia vastaan kohtisuora.
tangentti = sp.Matrix([-gP[1], gP[0]])
print("grad . tangentti =", gP.dot(tangentti))
# @loppu tasa-arvo
