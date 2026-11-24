"""CORDICin tarkkuus kierrosten määrän funktiona.

Käyttö: python3 analyysit/cordic_tarkkuus.py
"""

from __future__ import annotations

import math
import random

from malli.cordic import ROTAATIO, cordic
from malli.kertoimet import cordic_vahvistus


# @alku tarkkuus
def suurin_virhe(kierrokset: int, kulmat: list[int]) -> float:
    """Suurin cos- ja sin-virhe Q1.15:n LSB:inä. Alkupiste 1/K
    lasketaan samalle kierrosmäärälle, joten vahvistus kumoutuu."""
    x0 = round((1 << 15) / cordic_vahvistus(kierrokset))
    suurin = 0.0
    for z in kulmat:
        x, y, _ = cordic(ROTAATIO, x0, 0, z, kierrokset)
        theta = 2 * math.pi * z / (1 << 16)
        for arvo, tarkka in ((x, math.cos(theta)), (y, math.sin(theta))):
            suurin = max(suurin, abs(arvo / 4 - tarkka * (1 << 15)))
    return suurin


def main() -> None:
    rng = random.Random(1)
    kulmat = [rng.randint(-(1 << 15), (1 << 15) - 1) for _ in range(2000)]
    print("kierrokset  K          suurin virhe  tarkkuus")
    for n in (2, 4, 6, 8, 10, 12, 14, 16):
        v = suurin_virhe(n, kulmat)
        print(
            f"{n:9}  {cordic_vahvistus(n):.6f}  {v:9.2f} LSB  "
            f"{15 - math.log2(v):5.1f} bittiä"
        )
    # @loppu tarkkuus


if __name__ == "__main__":
    main()
