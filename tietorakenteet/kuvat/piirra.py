"""Piirtää tutoriaalin kuvaajat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut luetaan
esimerkkien testatuista tulosteista (esimerkit/*.odotettu).
"""

import re
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
KOROSTUS = "#B04848"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def kuormitus(polku: Path) -> None:
    """Kokeilut kuormituskertoimen funktiona (07-avoin.odotettu)."""
    teksti = (JUURI / "esimerkit/07-avoin.odotettu").read_text("utf-8")
    mitatut = [tuple(float(x) for x in m) for m in re.findall(
        r"alfa ([\d.]+): löytyy\s+([\d.]+) \(teoria\s+[\d.]+\), "
        r"ei löydy\s+([\d.]+)", teksti)]
    assert len(mitatut) >= 5, mitatut
    alfat = [i / 200 for i in range(20, 185)]
    fig = Figure(figsize=(6.0, 3.0), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(alfat, [0.5 * (1 + 1 / (1 - a)) for a in alfat], color=HARMAA,
            linewidth=1.2)
    ax.plot(alfat, [0.5 * (1 + 1 / (1 - a) ** 2) for a in alfat],
            color=KOROSTUS, linewidth=1.2)
    ax.plot([m[0] for m in mitatut], [m[1] for m in mitatut], "o",
            color=HARMAA, markersize=4)
    ax.plot([m[0] for m in mitatut], [m[2] for m in mitatut], "s",
            color=KOROSTUS, markersize=4)
    ax.annotate("avainta ei ole", (0.905, 51), xytext=(-8, 0),
                textcoords="offset points", ha="right", va="center",
                fontsize=8, color=KOROSTUS)
    ax.annotate("avain löytyy", (0.92, 6.7), xytext=(0, 6),
                textcoords="offset points", ha="right", fontsize=8,
                color=HARMAA)
    ax.axvline(0.75, color=VAALEA, linewidth=0.8, linestyle="--")
    ax.annotate("kasvatusraja 0,75", (0.75, 40), xytext=(-4, 0),
                textcoords="offset points", ha="right", fontsize=8,
                color=HARMAA)
    ax.set_xlabel("kuormituskerroin α")
    ax.set_ylabel("kokeiluja hakua kohti")
    ax.set_xlim(0.1, 0.93)
    ax.set_ylim(0, 60)
    ax.grid(True, which="major", color=VAALEA, linewidth=0.5)
    fig.savefig(polku / "kuormitus.png", metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    kuormitus(kohde)


if __name__ == "__main__":
    main()
