"""Tuntemattoman binääritiedoston tutkiminen.

Käyttö:
  python3 tutki.py heksa TIEDOSTO ALKU PITUUS
  python3 tutki.py entropia TIEDOSTO LOHKO
  python3 tutki.py merkkijonot TIEDOSTO PITUUS
  python3 tutki.py luvut TIEDOSTO

Komento luvut etsii 32-bittisiä little-endian-kokonaislukuja, jotka
näyttävät aikaleimoilta tai pituuskentiltä, sekä tarkistaa, onko
tiedoston lopussa CRC-32-tarkiste.
"""

import math
import re
import sys
import zlib
from collections import Counter
from datetime import UTC, datetime


def heksa(data: bytes, alku: int, pituus: int) -> None:
    """Heksavedos: siirtymä, 16 tavua ja tulostuvat merkit."""
    for rivi in range(alku, min(alku + pituus, len(data)), 16):
        osa = data[rivi:min(rivi + 16, alku + pituus)]
        tavut = " ".join(f"{b:02x}" for b in osa)
        merkit = "".join(chr(b) if 32 <= b < 127 else "." for b in osa)
        print(f"{rivi:06x}  {tavut:<47}  {merkit}")


def entropia(data: bytes, lohko: int) -> None:
    """Shannonin entropia biteinä tavua kohti lohkoittain."""
    for alku in range(0, len(data), lohko):
        osa = data[alku:alku + lohko]
        laskut = Counter(osa)
        h = -sum(n / len(osa) * math.log2(n / len(osa))
                 for n in laskut.values())
        print(f"{alku:06x}  {h:4.2f}  {'#' * round(h * 4)}")


def merkkijonot(data: bytes, pituus: int) -> None:
    """Vähintään `pituus` tulostuvan ASCII-merkin jonot."""
    for osuma in re.finditer(rb"[\x20-\x7e]{%d,}" % pituus, data):
        print(f"{osuma.start():06x}  {osuma.group().decode()}")


# @alku luvut
def luvut(data: bytes) -> None:
    """Aikaleimoilta ja pituuksilta näyttävät u32-arvot.

    Yksittäinen aikaleimaa muistuttava arvo on usein sattumaa, joten
    ehdokkaista (vuodet 2020-2034) etsitään pisin ketju, jossa aika
    kasvaa enintään vuorokauden ja tiedostosiirtymä vähintään neljä
    tavua kerrallaan: peräkkäisten tietueiden aikaleimat.
    """
    ehdokkaat = []
    for i in range(len(data) - 3):
        arvo = int.from_bytes(data[i:i + 4], "little")
        if 1_577_836_800 <= arvo < 2_051_222_400:
            ehdokkaat.append((i, arvo))
        elif 0 < arvo < len(data) and i + 4 + arvo + 4 == len(data):
            print(f"{i:06x}  u32 {arvo}: pituuskenttä? {arvo} tavua "
                  "ja 4 tavua loppuun")
    ketjut: list[list[tuple[int, int]]] = []
    for i, arvo in ehdokkaat:
        paras: list[tuple[int, int]] = []
        for ketju in ketjut:
            j, edellinen = ketju[-1]
            if i - j >= 4 and 0 < arvo - edellinen <= 86_400 and \
                    len(ketju) > len(paras):
                paras = ketju
        ketjut.append([*paras, (i, arvo)])
    pisin = max(ketjut, key=len, default=[])
    for n, (i, arvo) in enumerate(pisin):
        aika = datetime.fromtimestamp(arvo, UTC)
        vali = "" if n == 0 else \
            f"  +{i - pisin[n - 1][0]} tavua, +{arvo - pisin[n - 1][1]} s"
        print(f"{i:06x}  u32 aikaleima? {aika:%Y-%m-%d %H:%M} UTC{vali}")
    loppu = int.from_bytes(data[-4:], "little")
    if loppu == zlib.crc32(data[:-4]):
        print(f"{len(data) - 4:06x}  CRC-32 koko edeltävästä datasta")
# @loppu luvut


def main() -> None:
    komento, tiedosto = sys.argv[1], sys.argv[2]
    with open(tiedosto, "rb") as f:
        data = f.read()
    if komento == "heksa":
        heksa(data, int(sys.argv[3], 0), int(sys.argv[4], 0))
    elif komento == "entropia":
        entropia(data, int(sys.argv[3]))
    elif komento == "merkkijonot":
        merkkijonot(data, int(sys.argv[3]))
    elif komento == "luvut":
        luvut(data)
    else:
        sys.exit(f"tuntematon komento: {komento}")


if __name__ == "__main__":
    main()
