"""Miten kirjasto laskee e^x: välin supistus ja lyhyt Taylorin sarja."""

import math

# @alku exp
LN2 = math.log(2.0)


def oma_exp(x: float) -> tuple[float, int]:
    """e^x = 2^k e^r, missä x = k ln 2 + r ja |r| <= ln(2)/2.
    Pienellä r:llä Taylorin sarja suppenee nopeasti. Palauttaa arvon ja
    käytettyjen termien määrän."""
    k = round(x / LN2)
    r = x - k * LN2
    termi, summa, n = 1.0, 1.0, 0
    while abs(termi) > 1e-17 * abs(summa):
        n += 1
        termi *= r / n
        summa += termi
    return math.ldexp(summa, k), n          # summa * 2^k


for x in (0.1, 1.0, 10.0, -20.0, 300.0):
    arvo, termeja = oma_exp(x)
    suhteellinen = abs(arvo - math.exp(x)) / math.exp(x)
    print(f"exp({x:6}) = {arvo:.15e}  termejä {termeja:2d}  "
          f"ero {suhteellinen:.1e}")
# @loppu exp

# @alku suora
# Ilman välin supistusta sarja x = -20 kohdassa kumoutuu pahasti:
# termit ovat suurimmillaan ~4e7 ja tulos on ~2e-9.
termi, summa = 1.0, 1.0
for n in range(1, 120):
    termi *= -20.0 / n
    summa += termi
print(f"suora sarja exp(-20) = {summa:.3e}, oikea {math.exp(-20):.3e}")
# @loppu suora
