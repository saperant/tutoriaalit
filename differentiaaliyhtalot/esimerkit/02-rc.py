"""RC-piirin varautuminen: sama yhtälö kuin säiliöllä ja kahvilla."""

import sympy as sp

# @alku rc
# Kirchhoffin jännitelaki: U = R i + u_C ja i = C du_C/dt, joten
# RC du_C/dt + u_C = U. Ratkaistaan symboleilla ja sijoitetaan arvot
# U = 5 V, R = 10 kOhm, C = 100 nF vasta lopuksi.
t = sp.symbols("t", nonnegative=True)
U, R, C = sp.symbols("U R C", positive=True)
u = sp.Function("u")
ratkaisu = sp.dsolve(
    sp.Eq(R * C * u(t).diff(t) + u(t), U), u(t), ics={u(0): 0}
).rhs
print("u_C(t) =", ratkaisu)
arvot = {U: 5, R: 10_000, C: sp.Rational(1, 10_000_000)}
tau = (R * C).subs(arvot)
print("aikavakio:", tau, "s =", float(tau) * 1000, "ms")
# Milloin jännite ylittää logiikan kynnyksen 0,7 U?
aika = sp.solve(sp.Eq(ratkaisu, sp.Rational(7, 10) * U), t)[0]
suhde = sp.logcombine(sp.simplify(aika / (R * C)))
print("kynnys ylittyy, kun t / RC =", suhde)
print(
    f"eli {float(aika.subs(arvot)) * 1000:.3f} ms "
    f"= {float(aika.subs(arvot) / tau):.3f} tau"
)
# @loppu rc
