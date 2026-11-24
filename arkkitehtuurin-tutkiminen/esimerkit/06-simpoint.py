"""SimPoint-tyylinen näytteistys: koko ohjelman CPI muutaman
intervallin yksityiskohtaisella simuloinnilla.

Käyttö: python3 06-simpoint.py INTERVALLIT
"""

import sys
from pathlib import Path

from arkki.intervalli import simpoint

INTERVALLI = 1000


def main() -> None:
    # @alku luku
    jaksot, bbv = [], []
    for rivi in Path(sys.argv[1]).read_text("ascii").splitlines():
        j, *lohkot = (int(x) for x in rivi.split())
        jaksot.append(j)
        bbv.append(lohkot)
    cpi = [j / INTERVALLI for j in jaksot]
    tarkka = sum(jaksot) / (INTERVALLI * len(jaksot))
    # @loppu luku
    print(f"intervalleja {len(cpi)}, tarkka CPI {tarkka:.3f}")
    print(f"{'menetelmä':<22} {'CPI':>6} {'virhe':>7} {'simuloitu':>10}")

    def tulosta(nimi: str, arvio: float, n: int) -> None:
        print(f"{nimi:<22} {arvio:6.3f} {arvio / tarkka - 1:+7.1%}"
              f" {n / len(cpi):10.0%}")

    # @alku vertailu
    tulosta("alusta 5 intervallia", sum(cpi[:5]) / 5, 5)
    tasa = cpi[::20]
    tulosta("joka 20. intervalli", sum(tasa) / len(tasa), len(tasa))
    for k in (1, 2, 3, 4, 6):
        arvio, edustajat = simpoint(bbv, cpi, k)
        tulosta(f"SimPoint k = {k}", arvio, len(edustajat))
    # @loppu vertailu


if __name__ == "__main__":
    main()
