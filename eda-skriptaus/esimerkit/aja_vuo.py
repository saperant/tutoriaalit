"""Projektin vuo komentoriviltä; CI:n työt kutsuvat tätä.

    python3 aja_vuo.py --ajohak ajo sta       # vaiheet sta:han asti
    python3 aja_vuo.py --ajohak ajo --leveys 16
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vuo.kulku import projektin_vuo

JUURI = Path(__file__).resolve().parent


def main() -> int:
    jasennin = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    jasennin.add_argument("kohde", nargs="?", help="viimeinen vaihe")
    jasennin.add_argument("--ajohak", type=Path, default=Path("ajo"))
    jasennin.add_argument("--leveys", type=int, default=8)
    a = jasennin.parse_args()
    vuo = projektin_vuo(JUURI, a.ajohak.resolve(), leveys=a.leveys)
    tilat = vuo.aja(a.kohde, rinnakkain=2)
    for nimi, tila in tilat.items():
        print(f"{nimi:10} {tila}")
    return 0 if all(t in ("ajettu", "ajan tasalla")
                    for t in tilat.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
