"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
samoilla funktioilla kuin lukujen testatuissa esimerkeissä.
"""

import random
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))

from toimitus.haarat import Repo, kokeile
from toimitus.julkaisu import STRATEGIAT, Asetelma, simuloi

KOROSTUS = "#1D6F80"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 4.6, korkeus: float = 2.7) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def haaran_ika(polku: Path) -> None:
    """Ristiriidan todennäköisyys haaran iän ja rungon vilkkauden mukaan."""
    iat = list(range(1, 15))
    fig = uusi()
    ax = fig.add_subplot()
    for runko, vari in ((10, VAALEA), (20, KOROSTUS), (40, TOINEN)):
        repo = Repo(runko_paivassa=runko)
        osuudet = [kokeile(repo, ika, toistoja=1500)[0] * 100 for ika in iat]
        ax.plot(iat, osuudet, color=vari, linewidth=1.4, marker="o",
                markersize=3, label=f"runkoon {runko} riviä/pv")
    ax.set_xlabel("haaran ikä yhdistettäessä (pv)")
    ax.set_ylabel("ristiriidan todennäköisyys (%)")
    ax.set_ylim(0, 103)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, polku)


def epavakaa(polku: Path) -> None:
    """Putken läpimenon todennäköisyys epävakaiden testien määrän mukaan."""
    maarat = list(range(0, 301, 10))
    fig = uusi()
    ax = fig.add_subplot()
    for hairio, vari in ((0.001, VAALEA), (0.005, KOROSTUS), (0.01, TOINEN)):
        ax.plot(maarat, [(1 - hairio) ** n * 100 for n in maarat],
                color=vari, linewidth=1.4,
                label=f"testi pettää {hairio * 100:g} %:ssa ajoista"
                .replace(".", ","))
    ax.set_xlabel("epävakaita testejä putkessa")
    ax.set_ylabel("ehjä muutos menee läpi (%)")
    ax.set_ylim(0, 103)
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


def julkaisu(polku: Path) -> None:
    """Epäonnistuneiden pyyntöjen kertymä, kun uusi versio on rikki."""
    askelia = 6
    fig = uusi(4.8, 2.8)
    ax = fig.add_subplot()
    varit = (HARMAA, VAALEA, TOINEN, KOROSTUS)
    for strategia, vari in zip(STRATEGIAT, varit, strict=True):
        arpa = random.Random(1)
        summat = [0.0] * askelia
        for _ in range(300):
            kertyma = simuloi(strategia, Asetelma(), arpa).kertyma
            for i in range(askelia):
                summat[i] += kertyma[min(i, len(kertyma) - 1)]
        ax.plot(range(1, askelia + 1), [s / 300 for s in summat],
                color=vari, linewidth=1.4, marker="o", markersize=3,
                label=strategia.nimi)
    ax.set_xlabel("askel julkaisun alusta")
    ax.set_ylabel("epäonnistuneita pyyntöjä (kertymä)")
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


KUVAT = {"haaran-ika": haaran_ika, "epavakaa": epavakaa,
         "julkaisu": julkaisu}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"{nimi}.png")
