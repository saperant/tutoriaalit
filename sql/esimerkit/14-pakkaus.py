"""Aikasarjan pakkaus: delta-of-delta aikaleimoille ja XOR arvoille.

Laskee, montako bittiä Gorilla-tyyppinen koodaus (Facebook 2015, käytössä
mm. Prometheuksessa ja InfluxDB:ssä) tarvitsee verrattuna raakamuotoon,
jossa aikaleima ja arvo vievät kumpikin 64 bittiä.
"""

import math
import struct
from itertools import pairwise


# @alku aikaleimat
def delta_of_delta(ajat: list[int]) -> list[int]:
    """Ensimmäinen aika ja ensimmäinen ero sellaisinaan, sitten erojen
    erot. Tasaisella näytteenotolla lähes kaikki ovat nollia."""
    erot = [b - a for a, b in pairwise(ajat)]
    return [ajat[0], erot[0]] + [b - a for a, b in pairwise(erot)]


def palauta(koodi: list[int]) -> list[int]:
    ajat, ero = [koodi[0], koodi[0] + koodi[1]], koodi[1]
    for dd in koodi[2:]:
        ero += dd
        ajat.append(ajat[-1] + ero)
    return ajat


def bitit_ajalle(dd: int) -> int:
    """Gorillan vaihtuvapituinen koodi: etuliite ja arvo."""
    if dd == 0:
        return 1
    for etuliite, leveys in ((2, 7), (3, 9), (4, 12)):
        if -(1 << (leveys - 1)) <= dd < (1 << (leveys - 1)):
            return etuliite + leveys
    return 4 + 32
# @loppu aikaleimat


# @alku arvot
def bitit(x: float) -> int:
    return int.from_bytes(struct.pack(">d", x), "big")


def bitit_arvolle(edellinen: float, x: float) -> int:
    """XOR edelliseen: sama arvo 1 bitti, muuten merkitsevät bitit
    johtavien ja häntänollien väliltä (yksinkertaistettu Gorilla)."""
    xor = bitit(edellinen) ^ bitit(x)
    if xor == 0:
        return 1
    johtavat = 64 - xor.bit_length()
    hanta = (xor & -xor).bit_length() - 1
    return 2 + 5 + 6 + (64 - johtavat - hanta)
# @loppu arvot


# @alku mittaus
def main() -> None:
    # Minuutin välein mitattu lämpötila 0,1 asteen tarkkuudella; joka
    # 50. näyte myöhästyy kaksi sekuntia.
    ajat = [1_795_000_000 + 60 * n + (2 if n % 50 == 0 else 0)
            for n in range(1000)]
    arvot = [round(20 + 5 * math.sin(n / 30), 1) for n in range(1000)]

    koodi = delta_of_delta(ajat)
    assert palauta(koodi) == ajat
    nollia = sum(1 for dd in koodi[2:] if dd == 0)
    aikabitit = 64 + 64 + sum(bitit_ajalle(dd) for dd in koodi[2:])
    arvobitit = 64 + sum(bitit_arvolle(a, b) for a, b in pairwise(arvot))
    # Sama arvo kokonaislukuna (kymmenyksinä) ja delta-of-delta-koodilla.
    kymmenykset = [round(10 * a) for a in arvot]
    kokonaisbitit = 64 + 64 + sum(bitit_ajalle(dd) for dd
                                  in delta_of_delta(kymmenykset)[2:])
    raaka = len(ajat) * (64 + 64)
    print(f"näytteitä: {len(ajat)}")
    print(f"erojen erot nollia: {nollia} / {len(koodi) - 2}")
    print(f"aikaleimat: {aikabitit / len(ajat):.1f} bittiä/näyte")
    print(f"arvot XOR-koodilla: {arvobitit / len(arvot):.1f} bittiä/näyte")
    print("arvot kymmenyksinä, delta-of-delta: "
          f"{kokonaisbitit / len(arvot):.1f} bittiä/näyte")
    print(f"pakkaussuhde: {raaka / (aikabitit + arvobitit):.1f}")
# @loppu mittaus


if __name__ == "__main__":
    main()
