"""Shannonin entropia lohkoittain (bittiä tavua kohden, 0..8).

Käyttö: python3 entropia.py TIEDOSTO [LOHKO]  (oletus 512 tavua)

Teksti on tyypillisesti 4-5 bittiä, konekieli 5-6,5, pakattu tai
salattu data lähes 8 ja täyte (0x00 tai 0xFF) 0. Pienessä lohkossa
satunnainenkaan data ei yllä kahdeksaan: 512 tavun lohkon yläraja on
käytännössä noin 7,6.
"""
import math
import sys
from collections import Counter


def entropia(data: bytes) -> float:
    if not data:
        return 0.0
    maarat = Counter(data)
    return 0.0 - sum(m / len(data) * math.log2(m / len(data))
                     for m in maarat.values())


# @alku luokka
def luokka(arvo: float) -> str:
    if arvo < 1.0:
        return "täyte"
    if arvo > 7.2:
        return "pakattu tai salattu?"
    return ""
# @loppu luokka


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    lohko = int(sys.argv[2]) if len(sys.argv) > 2 else 512
    for alku in range(0, len(data), lohko):
        arvo = entropia(data[alku:alku + lohko])
        palkki = "#" * round(arvo * 4)
        rivi = f"{alku:06x} {arvo:4.2f} {palkki:<32} {luokka(arvo)}"
        print(rivi.rstrip())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
