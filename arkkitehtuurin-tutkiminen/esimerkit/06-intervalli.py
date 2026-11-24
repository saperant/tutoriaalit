"""Intervallimalli yksityiskohtaista ydinmallia vastaan.

Käyttö: python3 06-intervalli.py YDINMALLIN_TULOSTE KÄSKYVIRTA
"""

import sys
from pathlib import Path

from arkki.intervalli import Ydin, intervallimalli


def main() -> None:
    rivit = Path(sys.argv[1]).read_text("utf-8").splitlines()
    kaskyt = Path(sys.argv[2]).read_text("ascii").strip()
    print("CPI: yksityiskohtainen malli ja intervallimallin versiot")
    print(f"{'ikkuna':>6} {'tarkka':>7} {'ei limitystä':>13} {'limitys':>13}"
          f" {'+riippuvuus':>13}")
    for rivi in rivit[2:5]:
        ikkuna, _jaksot, cpi, perus = rivi.split()
        # @alku vertailu
        ydin = Ydin(int(ikkuna), float(perus))
        arviot = [intervallimalli(kaskyt, ydin, limitys=False),
                  intervallimalli(kaskyt, ydin, riippuvuudet=False),
                  intervallimalli(kaskyt, ydin)]
        tarkka = float(cpi)
        solut = [f"{a / len(kaskyt):.2f} {a / len(kaskyt) / tarkka - 1:+5.0%}"
                 for a in arviot]
        # @loppu vertailu
        print(f"{ikkuna:>6} {tarkka:7.3f}" + "".join(f"{s:>14}"
                                                     for s in solut))


if __name__ == "__main__":
    main()
