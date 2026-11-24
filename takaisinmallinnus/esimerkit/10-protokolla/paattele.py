"""Päättelee binääriprotokollan kentät liikennekaappauksesta.

Käyttö: python3 paattele.py KAAPPAUS

Kaappaus koostuu tietueista: suunta (1 tavu), pituus (u16 LE) ja kehys.
Skripti etsii kehyksistä vakiokentät, pituuskentän, järjestysnumeron,
pyynnön ja vastauksen tyyppien suhteen sekä tarkistesumman laskutavan,
ja purkaa lopuksi kaikki kehykset päätellyn rakenteen mukaan.
"""

import sys
from collections.abc import Callable
from functools import reduce
from itertools import pairwise

Kehys = tuple[int, bytes]

TARKISTEET: dict[str, Callable[[bytes], int]] = {
    "summa tavuista 0..n-2": lambda k: sum(k[:-1]) % 256,
    "summa tavuista 1..n-2": lambda k: sum(k[1:-1]) % 256,
    "xor tavuista 0..n-2": lambda k: reduce(lambda a, b: a ^ b, k[:-1]),
    "xor tavuista 1..n-2": lambda k: reduce(lambda a, b: a ^ b, k[1:-1]),
}


def lue(tiedosto: str) -> list[Kehys]:
    with open(tiedosto, "rb") as f:
        data = f.read()
    kehykset = []
    kohta = 0
    while kohta < len(data):
        suunta = data[kohta]
        pituus = int.from_bytes(data[kohta + 1:kohta + 3], "little")
        kehykset.append((suunta, data[kohta + 3:kohta + 3 + pituus]))
        kohta += 3 + pituus
    return kehykset


def paattele(kehykset: list[Kehys]) -> None:
    lyhin = min(len(k) for _, k in kehykset)
    for i in range(lyhin - 1):
        arvot = {k[i] for _, k in kehykset}
        if len(arvot) == 1:
            print(f"tavu {i}: aina {arvot.pop():#04x} (tahdistus?)")
        elif all(k[i] == len(k) - 5 for _, k in kehykset):
            print(f"tavu {i}: kehyksen pituus - 5 (hyötykuorman pituus)")
    pyynnot = [k for s, k in kehykset if s == 0]
    vastaukset = [k for s, k in kehykset if s == 1]
    parit = list(zip(pyynnot, vastaukset, strict=True))
    if all(v[1] == p[1] | 0x80 for p, v in parit):
        print("tavu 1: tyyppi, vastaus = pyyntö | 0x80")
    if all(v[2] == p[2] for p, v in parit) and all(
            b[2] == a[2] + 1 for a, b in pairwise(pyynnot)):
        print("tavu 2: järjestysnumero, kasvaa pyynnöittäin, vastaus "
              "kaiuttaa")
    for nimi, laske in TARKISTEET.items():
        if all(k[-1] == laske(k) for _, k in kehykset):
            print(f"viimeinen tavu: tarkiste = {nimi} (mod 256)")


def main() -> None:
    kehykset = lue(sys.argv[1])
    print(f"{len(kehykset)} kehystä")
    paattele(kehykset)
    print("puretut kehykset:")
    for suunta, k in kehykset:
        nuoli = "->" if suunta == 0 else "<-"
        data = k[4:-1]
        teksti = data.decode("ascii") if data and all(
            32 <= b < 127 for b in data) else data.hex(" ")
        print(f"  {nuoli} tyyppi {k[1]:#04x} nro {k[2]:#04x} "
              f"data [{teksti}]")


if __name__ == "__main__":
    main()
