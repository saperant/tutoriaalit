"""Epälineaarisen järjestelmän tasapainot Jacobin matriisilla."""

import sympy as sp

# @alku jacobi
# Vaimennettu heiluri: theta' = omega, omega' = -sin(theta) - 0,5 omega.
th, om = sp.symbols("theta omega", real=True)
f = sp.Matrix([om, -sp.sin(th) - sp.Rational(1, 2) * om])
J = f.jacobian([th, om])
print("J =", J.tolist())
for nimi, piste in (("alas", (0, 0)), ("ylös", (sp.pi, 0))):
    Jp = J.subs({th: piste[0], om: piste[1]})
    arvot = [sp.N(a, 4) for a in Jp.eigenvals()]
    jalki, det = Jp.trace(), Jp.det()
    if det < 0:
        laatu = "satulapiste: epästabiili"
    else:
        laatu = "stabiili" if jalki < 0 else "epästabiili"
    print(f"{nimi}: jälki {jalki}, det {det} -> {laatu}")
    print("  ominaisarvot:", sorted(arvot, key=sp.default_sort_key))
# @loppu jacobi
