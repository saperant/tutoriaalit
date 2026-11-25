"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä.
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

KOROSTUS = "#546676"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def strategiat(polku: Path) -> None:
    """Uuden version liikenneosuus ajan funktiona kolmella strategialla.

    Periaatekuva: rullaava päivitys neljällä podilla (yksi kerrallaan),
    sininen–vihreä kertavaihtona ja kanarialintu portain 5, 25, 50 ja
    100 %.
    """
    kayrat = {
        "rullaava (4 podia, yksi kerrallaan)":
            ([0, 2, 4, 6, 8, 12], [0, 25, 50, 75, 100, 100]),
        "sininen–vihreä (kertavaihto)":
            ([0, 6, 12], [0, 100, 100]),
        "kanarialintu (portaat mittareiden mukaan)":
            ([0, 1, 4, 7, 10, 12], [0, 5, 25, 50, 100, 100]),
    }
    fig = Figure(figsize=(5.4, 3.6), dpi=200, layout="constrained")
    akselit = fig.subplots(3, 1, sharex=True)
    for ax, (nimi, (ajat, osuudet)) in zip(akselit, kayrat.items(),
                                           strict=True):
        ax.step(ajat, osuudet, where="post", color=KOROSTUS, lw=1.6)
        ax.fill_between(ajat, osuudet, step="post", color=KOROSTUS,
                        alpha=0.15)
        ax.set_ylim(0, 110)
        ax.set_yticks([0, 50, 100])
        ax.set_title(nimi, loc="left", fontsize=9, color=HARMAA)
        ax.set_ylabel("uusi versio, %")
    akselit[1].annotate("vanha ympäristö jää\nvaralle paluuta varten",
                        xy=(6, 100), xytext=(7.2, 35), fontsize=8,
                        color=HARMAA,
                        arrowprops={"arrowstyle": "-", "color": HARMAA,
                                    "lw": 0.6})
    akselit[2].annotate("5 %: virhe näkyy\nharvoille", xy=(1, 5),
                        xytext=(1.6, 55), fontsize=8, color=HARMAA,
                        arrowprops={"arrowstyle": "-", "color": HARMAA,
                                    "lw": 0.6})
    akselit[-1].set_xlabel("aika käyttöönoton alusta (suhteellinen)")
    akselit[-1].set_xticks([])
    fig.savefig(polku, metadata=METATIEDOT)


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    strategiat(kohde / "11-strategiat.png")


if __name__ == "__main__":
    main()
