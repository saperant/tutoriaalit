"""Separoituvat yhtälöt ja ratkaisun räjähtäminen."""

import sympy as sp

t = sp.symbols("t")
y = sp.Function("y")

# @alku erottelu
# y' = t*y: erotellaan dy/y = t dt ja integroidaan molemmat puolet.
Y, T, C = sp.symbols("Y T C")
vasen = sp.integrate(1 / Y, Y)
oikea = sp.integrate(T, T)
print("integroitu:", sp.Eq(vasen, oikea + C))
ratk = sp.dsolve(sp.Eq(y(t).diff(t), t * y(t)), y(t), ics={y(0): 1})
print("dsolve:", ratk.rhs)
print("tarkistus:", sp.checkodesol(sp.Eq(y(t).diff(t), t * y(t)), ratk))
# @loppu erottelu

# @alku rajahtaa
# y' = y^2, y(0) = 1: ratkaisu 1/(1 - t) kasvaa rajatta jo hetkellä 1,
# vaikka yhtälö on siisti kaikkialla.
rajahtaa = sp.dsolve(sp.Eq(y(t).diff(t), y(t) ** 2), y(t), ics={y(0): 1}).rhs
print("y' = y^2:", rajahtaa)
print("raja-arvo t -> 1-:", sp.limit(rajahtaa, t, 1, "-"))
# @loppu rajahtaa
