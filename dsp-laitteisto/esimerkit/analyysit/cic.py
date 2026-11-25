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


# @alku kompensointi
def kompensaattori(asteet: int, r: int, f0: float = 0.25) -> list[float]:
    """Kolmen kertoimen CFIR [a, 1 - 2a, a] ulostulon näytetaajuudella.
    Vaste on 1 - 2a(1 - cos 2 pi f); a valitaan niin, että CIC:n taipuma
    kumoutuu taajuudella f0 (ulostulon näytetaajuuden osina)."""
    a = (1 - 1 / vaste(f0 / r, asteet, r)) / (
        2 * (1 - math.cos(2 * math.pi * f0))
    )
    return [a, 1 - 2 * a, a]


def cfir_vaste(h: list[float], f: float) -> float:
    return h[1] + 2 * h[0] * math.cos(2 * math.pi * f)
    # @loppu kompensointi


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
    h = kompensaattori(n, r)
    print("kompensaattori [a, 1 - 2a, a], a = " + f"{h[0]:.4f}:")
    for f in (0.05, 0.125, 0.2, 0.25):
        ilman = 20 * math.log10(vaste(f / r, n, r))
        kanssa = ilman + 20 * math.log10(cfir_vaste(h, f))
        print(
            f"  f = {f:5.3f}: CIC {ilman:5.2f} dB, "
            f"kompensoitu {kanssa:5.2f} dB"
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
