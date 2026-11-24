"""Tiivistää Verilatorin koodikattavuuden yhdelle lähdetiedostolle.

Verilator kirjoittaa kattavuuden tiedostoon (coverage.dat), jossa
jokainen rivi on yksi kattavuuspiste ja sen osumamäärä. Tämä työkalu
yhdistää yhden tai useamman ajon tiedostot (osumat lasketaan yhteen),
laskee osuuden lajeittain ja luettelee pisteet, joihin ei osuttu.
Samaan pystyy verilator_coverage, mutta sen raportti kattaa kaikki
tiedostot testipenkki mukaan lukien.

Käyttö:
  python3 tyokalut/koodikattavuus.py --tiedosto rtl/fifo.sv AJO.dat...
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

LAJIT = {"v_line": "rivit", "v_branch": "haarat", "v_toggle": "bitit"}


# @alku lue
def lue(polut: list[Path]) -> dict[tuple[str, ...], int]:
    """Palauttaa osumat avaimella (tiedosto, laji, rivi, kohde)."""
    osumat: dict[tuple[str, ...], int] = defaultdict(int)
    for polku in polut:
        for rivi in polku.read_text().splitlines():
            m = re.fullmatch(r"C '(.*)' (\d+)", rivi)
            if not m:
                continue  # otsikkorivi
            # Kentät erotetaan merkeillä 0x01 ja nimi arvosta 0x02.
            kentat = dict(k.split("\x02", 1) for k in m[1].split("\x01") if k)
            laji = kentat["page"].split("/")[0]
            avain = (kentat["f"], laji, kentat["l"], kentat["o"])
            osumat[avain] += int(m[2])
    return osumat
    # @loppu lue


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tiedosto", required=True)
    p.add_argument("ajot", nargs="+", type=Path)
    a = p.parse_args()

    osumat = {k: v for k, v in lue(a.ajot).items() if k[0] == a.tiedosto}
    print(f"{a.tiedosto}, {len(a.ajot)} ajoa")
    # @alku yhteenveto
    for laji, nimi in LAJIT.items():
        pisteet = [v for k, v in osumat.items() if k[1] == laji]
        katettu = sum(1 for v in pisteet if v > 0)
        osuus = 100.0 * katettu / len(pisteet) if pisteet else 100.0
        print(f"  {nimi:<7} {katettu:>3}/{len(pisteet):<3} {osuus:5.1f} %")
    # @loppu yhteenveto

    # Kattamattomat bitit ryhmitellään signaaleittain.
    bitit: dict[str, list[str]] = defaultdict(list)
    muut: list[str] = []
    for (_, laji, rivi, kohde), maara in sorted(
        osumat.items(), key=lambda x: (x[0][1], int(x[0][2]), x[0][3])
    ):
        if maara > 0:
            continue
        if laji == "v_toggle":
            m = re.fullmatch(r"(.*)\[(\d+)\]", kohde)
            signaali, bitti = (m[1], m[2]) if m else (kohde, "0")
            bitit[signaali].append(bitti)
        else:
            muut.append(f"  rivi {rivi}: {LAJIT.get(laji, laji)} {kohde}")
    if muut or bitit:
        print("kattamatta:")
    for rivi in muut:
        print(rivi)
    for signaali, luettelo in bitit.items():
        print(f"  bitti {signaali}: {' '.join(luettelo)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
