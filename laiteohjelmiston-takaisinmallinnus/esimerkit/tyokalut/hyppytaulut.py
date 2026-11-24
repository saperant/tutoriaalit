"""Hyppytaulut (tbb): switch-lauseiden tapaukset.

Käyttö: python3 hyppytaulut.py KUVA KANTA TAULU LOPPU
"""
import sys

import thumb
from kuva import Kuva


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    taulu, loppu = int(sys.argv[3], 0), int(sys.argv[4], 0)
    funktiot = thumb.kaikki_funktiot(kuva, taulu, 32, (taulu, loppu))
    for osoite, f in sorted(funktiot.items()):
        for kasky, kohteet in sorted(f.hyppytaulut.items()):
            print(f"funktio {osoite:#x}, tbb osoitteessa {kasky:#x}:")
            for i, kohde in enumerate(kohteet):
                print(f"  tapaus {i}: {kohde:#x}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
