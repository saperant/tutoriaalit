"""Eulerin kaava sarjasta ja raja-arvosta."""

import cmath
import math


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku sarja
def exp_sarja(z: complex, termejä: int) -> complex:
    """Eksponenttifunktion sarjan osasumma: sum z^k / k!."""
    summa, termi = 0j, 1 + 0j
    for k in range(termejä):
        summa += termi
        termi *= z / (k + 1)          # z^(k+1)/(k+1)! edellisestä
    return summa


theta = 2.0
tarkka = complex(math.cos(theta), math.sin(theta))
for n in [2, 4, 8, 12, 16, 20]:
    virhe = abs(exp_sarja(1j * theta, n) - tarkka)
    print(f"{n:2d} termiä: {kl(exp_sarja(1j * theta, n))}"
          f"  virhe {virhe:.1e}")
# @loppu sarja

# @alku raja
# Yhtälö z' = i z alkuarvolla z(0) = 1: askel h kertoo luvulla (1 + i h).
for n in [10, 100, 1000, 10000]:
    z = (1 + 1j * theta / n) ** n
    print(f"n = {n:5d}: |z| = {abs(z):.5f}, kulma = {cmath.phase(z):.5f},"
          f" virhe {abs(z - tarkka):.1e}")
# @loppu raja
