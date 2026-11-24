"""Kaaren pituus ja pyörähdyskappaleen tilavuus integraalina."""

import math

import sympy as sp
from scipy import integrate

x, R, H = sp.symbols("x R H", positive=True)

# @alku kaari
# Kaaren pituus: s = int sqrt(1 + f'(x)^2) dx. Esimerkkinä riippusillan
# kaapelin muotoa approksimoiva paraabeli y = x^2/400, jänneväli 200 m.
f = x**2 / 400
integroitava = sp.sqrt(1 + sp.diff(f, x) ** 2)
s = sp.integrate(integroitava, (x, -100, 100))
print("kaapelin pituus:", sp.N(s, 6), "m")
arvo, _ = integrate.quad(lambda t: math.sqrt(1 + (t / 200) ** 2),
                         -100, 100)
print(f"quad: {arvo:.4f} m")
# @loppu kaari

# @alku tilavuus
# Pyörähdyskappale: käyrä y = f(x) pyörii x-akselin ympäri;
# V = pi int f(x)^2 dx (kiekkomenetelmä).
kartio = sp.pi * sp.integrate((R * x / H) ** 2, (x, 0, H))
pallo = sp.pi * sp.integrate(R**2 - x**2, (x, -R, R))
print("kartio:", sp.factor(kartio), "; pallo:", sp.factor(pallo))
# @loppu tilavuus
