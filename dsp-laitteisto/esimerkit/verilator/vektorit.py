"""Kirjoittaa Verilator-testipenkille satunnaisen sisääntulon ja mallin
ulostulon tekstitiedostoihin.

Käyttö: python3 verilator/vektorit.py HAKEMISTO [N]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from malli.kertoimet import DATA_BITIT, FIR, KERROIN_MURTO
from malli.kiintea import alue
from malli.suotimet import fir


def main() -> int:
    hakemisto = Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 100_000
    hakemisto.mkdir(parents=True, exist_ok=True)
    rng = random.Random(1)
    pienin, suurin = alue(DATA_BITIT)
    # Puolet tasajakautuneita, puolet ääriarvoja: saturaatio mukana.
    x = [
        rng.randint(pienin, suurin)
        if rng.random() < 0.5
        else rng.choice((pienin, suurin))
        for _ in range(n)
    ]
    y = fir(x, FIR, KERROIN_MURTO, DATA_BITIT)
    (hakemisto / "syote.txt").write_text("\n".join(map(str, x)) + "\n")
    (hakemisto / "odotettu.txt").write_text("\n".join(map(str, y)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
