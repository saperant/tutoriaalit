"""Numeerisen raja-arvon sudenkuopat: kumoutuminen ja pyöristys."""

import math

# @alku kumoutuminen
# (1 - cos x)/x^2 -> 1/2, kun x -> 0. Suora kaava liukuluvuilla:
for k in range(1, 10, 2):
    h = 10.0**-k
    suora = (1 - math.cos(h)) / h**2
    # Sama lauseke ilman vähennyslaskua: 1 - cos h = 2 sin^2(h/2).
    vakaa = 2 * math.sin(h / 2) ** 2 / h**2
    print(f"h=1e-{k}: suora {suora:.10f}  vakaa {vakaa:.10f}")
# @loppu kumoutuminen

# @alku e
# (1 + 1/n)^n -> e. Kun n kasvaa, 1/n hukkuu ykkösen pyöristykseen.
for k in (4, 8, 12, 16):
    n = 10.0**k
    print(f"n=1e{k}: {(1 + 1 / n) ** n:.12f}")
print(f"e     = {math.e:.12f}")
print(f"log1p, n=1e8: {math.exp(1e8 * math.log1p(1e-8)):.12f}")
# @loppu e
