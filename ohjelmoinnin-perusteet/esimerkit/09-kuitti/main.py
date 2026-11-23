"""Lukee ostokset muodossa nimi;määrä;hinta ja tulostaa kuitin."""

import sys

from rahat import euroina, jasenna_summa


def main() -> int:
    yhteensa = 0
    for rivi in sys.stdin:
        nimi, maara, hinta = rivi.strip().split(";")
        rivin_hinta = int(maara) * jasenna_summa(hinta)
        yhteensa += rivin_hinta
        print(f"{nimi:<14}{maara:>3} x {hinta:>6}{euroina(rivin_hinta):>10}")
    print(f"{'Yhteensä':<26}{euroina(yhteensa):>10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
