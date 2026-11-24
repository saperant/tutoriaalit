"""Paloittain määritelty funktio: porrastettu siirtohinta."""

import sympy as sp

k = sp.symbols("k", nonnegative=True)   # kulutus, kWh kuukaudessa

# @alku paloittain
# Kuvitteellinen tariffi: 8 c/kWh 300 kWh:iin asti, sen jälkeen 6 c/kWh,
# ja perusmaksu 5 euroa. Hinta euroina.
hinta = sp.Piecewise(
    (5 + sp.Rational(8, 100) * k, k <= 300),
    (5 + 24 + sp.Rational(6, 100) * (k - 300), True),
)
for kulutus in [0, 150, 300, 301, 1000]:
    print(f"{kulutus:5d} kWh: {float(hinta.subs(k, kulutus)):7.2f} eur")
# @loppu paloittain

# @alku jatkuvuus
vasen = sp.limit(hinta, k, 300, dir="-")
oikea = sp.limit(hinta, k, 300, dir="+")
print("raja-arvot kohdassa 300:", vasen, oikea, "jatkuva:", vasen == oikea)
# @loppu jatkuvuus

# @alku kaanteinen
# Kuinka paljon voi kuluttaa 50 eurolla?
print("50 eurolla:", sp.solve(sp.Eq(hinta, 50), k), "kWh")
# @loppu kaanteinen
