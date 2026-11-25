"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Taulukon jaon kuva
lasketaan luvun 7 taulukon kaavoista (alkio i pankissa i mod F tai
i / (koko / F)) ja esimerkin 07-matriisi lukukuvioista.
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

KOROSTUS = "#B04848"          # alueen Laitteistosuunnittelu väri
PANKIT = ["#F0DADA", "#D5E6EE", "#F1E3CC", "#DCE8D4"]
HARMAA = "#5B6B70"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["text.color"] = MUSTE
N, F = 4, 4                    # 4 x 4 -matriisi, neljä pankkia


def ruudukko(ax: Axes, otsikko: str, pankki: list[int],
             luettavat: list[int]) -> None:
    """16 alkiota matriisin muodossa: väri on pankki, kehys kierroksen
    lukemat alkiot."""
    ax.set_axis_off()
    ax.set_xlim(-0.1, N + 0.1)
    ax.set_ylim(N + 0.1, -0.75)
    ax.set_aspect("equal")
    ax.set_title(otsikko, fontsize=8)
    for i in range(N * N):
        rivi, sarake = divmod(i, N)
        ax.add_patch(Rectangle((sarake, rivi), 1, 1,
                               facecolor=PANKIT[pankki[i]],
                               edgecolor=HARMAA, linewidth=0.6))
        ax.text(sarake + 0.5, rivi + 0.42, str(i), ha="center",
                va="center", fontsize=8)
        ax.text(sarake + 0.5, rivi + 0.8, f"pankki {pankki[i]}",
                ha="center", va="center", fontsize=5, color=HARMAA)
    for i in luettavat:
        rivi, sarake = divmod(i, N)
        ax.add_patch(Rectangle((sarake + 0.05, rivi + 0.05), 0.9, 0.9,
                               facecolor="none", edgecolor=KOROSTUS,
                               linewidth=1.8))
    samat = len({pankki[i] for i in luettavat}) < len(luettavat)
    ax.text(N / 2, -0.3, "neljä lukua samasta pankista" if samat
            else "jokainen luku eri pankista", ha="center", fontsize=7,
            color=KOROSTUS if samat else MUSTE)


def jako(polku: Path) -> None:
    syklinen = [i % F for i in range(N * N)]
    lohko = [i // (N * N // F) for i in range(N * N)]
    rivi = [N * 1 + k for k in range(N)]          # A: rivi i = 1
    sarake = [N * k + 2 for k in range(N)]        # B: sarake j = 2
    fig = Figure(figsize=(6.4, 2.1), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 4)
    ruudukko(akselit[0], "A, syklinen jako", syklinen, rivi)
    ruudukko(akselit[1], "A, lohkojako", lohko, rivi)
    ruudukko(akselit[2], "B, syklinen jako", syklinen, sarake)
    ruudukko(akselit[3], "B, lohkojako", lohko, sarake)
    fig.savefig(polku, metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    jako(kohde / "jako.png")
    print("jako.png")


if __name__ == "__main__":
    main()
