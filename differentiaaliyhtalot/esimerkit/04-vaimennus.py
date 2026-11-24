"""Vaimennettu värähtelijä: karakteristinen yhtälö ja kolme tapausta."""

import sympy as sp

t = sp.symbols("t", nonnegative=True)
y = sp.Function("y")
lam = sp.symbols("lambda")

# @alku tapaukset
# m y'' + c y' + k y = 0, m = 1 kg, k = 4 N/m. Vaimennus c ratkaisee,
# millaisia karakteristisen yhtälön m l^2 + c l + k = 0 juuret ovat.
m, k = 1, 4
for c, nimi in (
    (1, "alivaimennettu"),
    (4, "kriittinen"),
    (5, "ylivaimennettu"),
):
    juuret = sp.roots(m * lam**2 + c * lam + k, lam)
    ratk = sp.dsolve(
        m * y(t).diff(t, 2) + c * y(t).diff(t) + k * y(t),
        y(t),
        ics={y(0): 1, y(t).diff(t).subs(t, 0): 0},
    ).rhs
    zeta = sp.Rational(c, 2) / sp.sqrt(m * k)
    print(f"c = {c} ({nimi}, zeta = {zeta}):")
    kuvaus = ", ".join(
        f"{j} (kerta {kerta})"
        for j, kerta in sorted(
            juuret.items(), key=lambda p: sp.default_sort_key(p[0])
        )
    )
    print("  juuret:", kuvaus)
    print("  y(t) =", sp.simplify(ratk))
# @loppu tapaukset
