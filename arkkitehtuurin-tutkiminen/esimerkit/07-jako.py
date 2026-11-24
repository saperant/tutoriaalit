"""Kiihdyttimen hyötymalli ja vertailu virtuaaliprototyyppiin.

Käyttö: python3 07-jako.py PROTOTYYPIN_TULOSTE
"""

import math
import sys
from dataclasses import dataclass, replace
from pathlib import Path

from arkki.mallit import amdahl


# @alku malli
@dataclass(frozen=True)
class Jako:
    sw_nayte: float = 42.0  # ns näytettä kohden ohjelmistona
    asetus: float = 16.0  # neljä rekisterikirjoitusta väylän yli
    huuhtelu: float = 0.5  # ns näytettä kohden (2 * 4 B / 64 B * 4 ns)
    pala: int = 16  # näytettä DMA-siirrossa
    siirto: float = 30.0  # ns: väylä 2 + muisti 20 + purske 8
    laskenta: float = 1.0  # ns näytettä kohden kiihdyttimessä
    tyhjennys: float = 16.0  # liukuhihnan viive
    keskeytys: float = 2000.0  # käyttöjärjestelmän keskeytyskäsittely
    kaksoispuskuri: bool = False

    def ohjelmisto(self, n: int) -> float:
        return n * self.sw_nayte

    def laitteisto(self, n: int) -> float:
        palat = math.ceil(n / self.pala)
        laskenta = self.pala * self.laskenta
        if self.kaksoispuskuri:  # siirrot ja laskenta limittäin
            pala = max(2 * self.siirto, laskenta)
        else:
            pala = 2 * self.siirto + laskenta
        return (self.asetus + n * self.huuhtelu + palat * pala
                + self.tyhjennys + self.keskeytys)

    def tasapiste(self) -> int:
        """Pienin n, jolla kiihdytin on nopeampi."""
        n = 1
        while self.laitteisto(n) >= self.ohjelmisto(n):
            n += 1
        return n
# @loppu malli


def main() -> None:
    malli = Jako()
    # @alku vertailu
    print(f"{'n':>6} {'malli us':>9} {'prototyyppi us':>15} {'ero':>6}")
    for rivi in Path(sys.argv[1]).read_text("utf-8").splitlines()[1:]:
        n, _sw, hw, *_ = rivi.split()
        arvio = malli.laitteisto(int(n)) / 1000
        print(f"{n:>6} {arvio:9.3f} {float(hw):15.3f}"
              f" {arvio / float(hw) - 1:+6.1%}")
    # @loppu vertailu
    # @alku vaihtoehdot
    vaihtoehdot = {
        "nykyinen": malli,
        "kysely (200 ns)": replace(malli, keskeytys=200.0),
        "kaksoispuskuri": replace(malli, kaksoispuskuri=True),
        "molemmat": replace(malli, keskeytys=200.0, kaksoispuskuri=True),
    }
    print(f"\n{'vaihtoehto':<16} {'tasapiste':>9} {'nopeutus n=4096':>16}"
          f" {'sovellus p=0.6':>15}")
    for nimi, m in vaihtoehdot.items():
        s = m.ohjelmisto(4096) / m.laitteisto(4096)
        print(f"{nimi:<16} {m.tasapiste():>9} {s:16.2f}"
              f" {amdahl(0.6, s):15.2f}")
    # @loppu vaihtoehdot


if __name__ == "__main__":
    main()
