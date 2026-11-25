"""Malliratkaisu 09-3: Modulista ohjelmaksi."""

import sys


def pinta_ala(leveys: float, korkeus: float) -> float:
    """Palauttaa suorakulmion pinta-alan."""
    return leveys * korkeus


def main() -> int:
    leveys = float(input())
    korkeus = float(input())
    print(f"Pinta-ala: {pinta_ala(leveys, korkeus)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
