"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Uudelleenyritysten
jakauma lasketaan samalla generaattorilla ja samalla siemenellä kuin
esimerkissä 10-uudelleenyritys.c, ja tulos tarkistetaan esimerkin
testattua tulostetta (10-uudelleenyritys.odotettu) vasten.
"""

import re
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#3D5A73"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
HAALEA = "#EEF1F2"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 8
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA
rcParams["grid.color"] = HAALEA
MASKI = (1 << 64) - 1


class Satunnainen:
    """xorshift64*, sama kuin otsakkeessa verkko.h."""

    def __init__(self, siemen: int) -> None:
        self.tila = siemen

    def alle(self, n: int) -> int:
        self.tila ^= self.tila >> 12
        self.tila ^= (self.tila << 25) & MASKI
        self.tila ^= self.tila >> 27
        luku = (self.tila * 0x2545F4914F6CDD1D) & MASKI
        return (luku >> 32) % n


def viive_ms(k: int, s: Satunnainen) -> int:
    """Sama kuin esimerkin viive_ms: täysi satunnaisuus."""
    perus, katto = 100, 5000
    raja = katto if k >= 7 else min(katto, perus << (k - 1))
    return s.alle(raja)


def uudelleenyritys(polku: Path) -> None:
    odotettu = (ESIMERKIT / "10-uudelleenyritys.odotettu").read_text("utf-8")
    ajat = [int(t) for t in re.findall(r"t = +(\d+) ms", odotettu)]
    pahimmat = [int(n) for n in re.findall(r"jaksossa (\d+) yrit", odotettu)]
    s = Satunnainen(99)
    nyt, omat = 0, [0]
    for k in range(1, len(ajat)):            # esimerkin ensimmäinen osa
        nyt += viive_ms(k, s)
        omat.append(nyt)
    assert omat == ajat, (omat, ajat)
    jakaumat = []
    for satunnaisesti in (False, True):
        jaksot = [0] * 200
        for _ in range(1000):
            t = sum(viive_ms(k, s) if satunnaisesti else 100 << (k - 1)
                    for k in range(1, 5))
            jaksot[t // 50] += 1
        jakaumat.append(jaksot)
    assert [max(j) for j in jakaumat] == pahimmat, pahimmat

    fig = Figure(figsize=(5.2, 2.9), dpi=200, layout="constrained")
    ylempi, alempi = fig.subplots(2, 1, sharex=True)
    x = [50 * j for j in range(40)]
    for ax, jaksot, vari, nimi in (
            (ylempi, jakaumat[0], TOINEN, "ilman satunnaisuutta"),
            (alempi, jakaumat[1], KOROSTUS, "täysi satunnaisuus")):
        ax.bar(x, jaksot[:40], width=46, align="edge", color=vari)
        ax.set_title(f"{nimi}: pahimmassa jaksossa {max(jaksot)} yritystä",
                     fontsize=8, loc="left")
        ax.set_ylabel("yrityksiä")
        ax.grid(True, axis="y")
        ax.set_axisbelow(True)
    alempi.set_xlabel("aika yhteyden katkeamisesta (ms), 50 ms:n jaksot")
    alempi.set_xlim(0, 2000)
    fig.savefig(polku, metadata={"Software": None})


KUVAT = {"uudelleenyritys": uudelleenyritys}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    for kuva in sys.argv[2:] or list(KUVAT):
        KUVAT[kuva](kohde / f"{kuva}.png")
