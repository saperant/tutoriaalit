"""Etsii, minkä alueen tarkiste kenttä on.

Käyttö: python3 tarkistehaku.py TIEDOSTO --kentat O... --alueet N:A:P...

Jokaista kenttää (u32 siirtymässä O) verrataan jokaisen alueen (nimi N,
alku A, pituus P) tarkisteisiin usealla algoritmilla. Jos kenttä on
itse alueen sisällä, se nollataan laskennan ajaksi; näin toimii moni
otsake, joka sisältää oman tarkisteensa. zlib-alkuiselle alueelle
kokeillaan myös puretun datan tarkistetta.
"""
import argparse
import struct
import zlib
from collections.abc import Callable

ALGORITMIT: dict[str, Callable[[bytes], int]] = {
    "crc32": zlib.crc32,
    "adler32": zlib.adler32,
    "summa32": lambda d: sum(d) & 0xFFFFFFFF,
}


def main() -> None:
    jasennin = argparse.ArgumentParser()
    jasennin.add_argument("tiedosto")
    jasennin.add_argument("--kentat", nargs="+", required=True)
    jasennin.add_argument("--alueet", nargs="+", required=True)
    argumentit = jasennin.parse_args()
    with open(argumentit.tiedosto, "rb") as f:
        data = f.read()
    alueet = []
    for teksti in argumentit.alueet:
        nimi, alku, pituus = teksti.split(":")
        alueet.append((nimi, int(alku, 0), int(pituus, 0)))
    # @alku haku
    for kentta in (int(k, 0) for k in argumentit.kentat):
        arvo, = struct.unpack_from("<I", data, kentta)
        osumat = []
        for nimi, alku, pituus in alueet:
            osa = bytearray(data[alku:alku + pituus])
            if alku <= kentta < alku + pituus:
                osa[kentta - alku:kentta - alku + 4] = bytes(4)
                nimi += " (kenttä nollana)"
            versiot = [(nimi, bytes(osa))]
            if osa[:1] == b"\x78":
                versiot.append((nimi + " purettuna",
                                zlib.decompress(bytes(osa))))
            for selite, tavut in versiot:
                for algoritmi, laske in ALGORITMIT.items():
                    if laske(tavut) == arvo:
                        osumat.append(f"{algoritmi}({selite})")
        print(f"{kentta:#06x} = {arvo:08x}: {', '.join(osumat) or '-'}")
    # @loppu haku


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
