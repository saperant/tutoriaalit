"""Suorituskyvyn vertailu versioiden valilla emuloimalla.

Kaytto: python3 mittaa.py FLASH_A FLASH_B FUNKTIO

Ajaa saman funktion kummastakin flash-kuvasta samoilla argumenteilla
ja vertaa kaskyjen maaraa. Nain loytyy suorituskykyregressio
binaarista: 2.4.1:n suodatusfunktio kaantyi vahingossa ilman
optimointeja (optimize("O0") -attribuutti jai koodiin).
"""
import struct
import sys

import emu

PUSKURI = 0x20008000
TULOS = 0x20008100


def aja(flash_polku: str, funktio: int) -> tuple[int, int]:
    with open(flash_polku, "rb") as f:
        laite = emu.Laite(f.read())
    naytteet = struct.pack("<8h", 100, 102, 98, 101, 99, 100, 103, 97)
    laite.kirjoita(PUSKURI, naytteet)
    # suodata(naytteet, n=8, ikkuna=4, tulos)
    paluu = laite.kutsu(funktio, PUSKURI, 8, 4, TULOS)
    return paluu, laite.kaskyja


def main() -> None:
    flash_a, flash_b, funktio = sys.argv[1], sys.argv[2], int(sys.argv[3], 0)
    paluu_a, kaskyt_a = aja(flash_a, funktio)
    paluu_b, kaskyt_b = aja(flash_b, funktio)
    print(f"A: paluu {paluu_a}, {kaskyt_a} kaskya")
    print(f"B: paluu {paluu_b}, {kaskyt_b} kaskya")
    if paluu_a == paluu_b:
        print(f"sama tulos, A kayttaa {kaskyt_a / kaskyt_b:.1f}x kaskyja")


if __name__ == "__main__":
    main()
