"""Tarkistaa syötteen viitenumerot rivi kerrallaan."""

import sys

from viite import on_kelvollinen


def main() -> int:
    virheita = 0
    for rivi in sys.stdin:
        viite = rivi.strip()
        if on_kelvollinen(viite):
            print(f"{viite:<22} kelvollinen")
        else:
            print(f"{viite:<22} VIRHEELLINEN")
            virheita += 1
    print(f"Virheellisiä: {virheita}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
