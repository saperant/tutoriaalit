"""CIC-desimaattorin bittikasvu, taajuusvaste ja kiertävän laskennan
oikeellisuus.

Käyttö: python3 analyysit/cic.py
"""

from __future__ import annotations

import math
import random

from malli import kertoimet as k
from malli.suotimet import cic


# @alku hogenauer
def kasvu(asteet: int, r: int, m: int = 1) -> int:
    """Hogenauerin bittikasvu: N log2(R M), kun R M on kahden potenssi."""
    return asteet * math.ceil(math.log2(r * m))


def vaste(f: float, asteet: int, r: int) -> float:
    """|H(f)| / R**N, f sisääntulon näytetaajuuden osina."""
    if f == 0:
        return 1.0
    return (
        abs(math.sin(math.pi * f * r) / (r * math.sin(math.pi * f))) ** asteet
    )
    # @loppu hogenauer


def main() -> None:
    print("bittikasvu N log2(R):")
    print("N   R=8  R=16  R=64")
    for n in range(1, 6):
        print(f"{n}  {kasvu(n, 8):4}  {kasvu(n, 16):4}  {kasvu(n, 64):4}")
    print()
    n, r = k.CIC_ASTEET, k.CIC_DESIMOINTI
    print(f"vaste, N = {n}, R = {r} (f ulostulon näytetaajuuden osina):")
    for f in (0.05, 0.125, 0.25, 0.5, 0.75):
        print(
            f"  f = {f:5.3f}: {20 * math.log10(vaste(f / r, n, r)):6.1f} dB"
        )
    print()
    # @alku kierto
    rng = random.Random(1)
    x = [rng.randint(-2048, 2047) for _ in range(4000)]
    kiertava = cic(x, n, r, k.CIC_SISAINEN, k.CIC_ULOS, kierto=True)
    rajaton = cic(x, n, r, k.CIC_SISAINEN, k.CIC_ULOS, kierto=False)
    eroja = sum(a != b for a, b in zip(kiertava, rajaton, strict=True))
    print(
        f"{k.CIC_SISAINEN}-bittinen kiertävä laskenta vs. rajattomat "
        f"kokonaisluvut: {eroja} eroa {len(kiertava)} näytteessä"
    )
    # Yksi bitti liian vähän: täysi askel ei mahdu ulostuloon.
    askel = [2047] * 400
    b = k.CIC_SISAINEN - 1
    lyhyt = cic(askel, n, r, b, k.CIC_ULOS, kierto=True)
    oikea = cic(askel, n, r, b, k.CIC_ULOS, kierto=False)
    vaarin = sum(a != c for a, c in zip(lyhyt, oikea, strict=True))
    print(
        f"{b} bittiä, täysi askel: {vaarin} eroa {len(lyhyt)} näytteessä, "
        f"viimeinen {lyhyt[-1]}, oikea {oikea[-1]}"
    )
    # @loppu kierto


if __name__ == "__main__":
    main()
