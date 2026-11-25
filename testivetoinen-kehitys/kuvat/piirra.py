"""Piirtää tutoriaalin kuvan. Käyttö: python3 kuvat/piirra.py

Kuva commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
luvun 5 esimerkin generaattorilla (esimerkit/05-parit/parit.py).
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(JUURI / "esimerkit" / "05-parit"))

from parit import parittaiset

KOROSTUS = "#1D6F80"      # alueen Työtavat ja ohjelmistotuotanto väri
HARMAA = "#5B6B70"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def parit(polku: Path) -> None:
    """Testien määrä, kun asetuksia on 2-8 ja jokaisella kolme arvoa."""
    asetuksia = list(range(2, 9))
    kaikki = [3 ** n for n in asetuksia]
    parittain = [
        len(parittaiset({f"a{i}": ["x", "y", "z"] for i in range(n)}))
        for n in asetuksia
    ]
    fig = Figure(figsize=(5.2, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(asetuksia, kaikki, "o-", color=HARMAA, linewidth=1.2,
            markersize=4, label="kaikki yhdistelmät")
    ax.plot(asetuksia, parittain, "o-", color=KOROSTUS, linewidth=1.6,
            markersize=4, label="parittainen joukko")
    for n, arvo in zip(asetuksia, parittain, strict=True):
        ax.annotate(str(arvo), (n, arvo), textcoords="offset points",
                    xytext=(0, -12), ha="center", fontsize=8,
                    color=KOROSTUS)
    ax.annotate(str(kaikki[-1]), (asetuksia[-1], kaikki[-1]),
                textcoords="offset points", xytext=(-6, 4), ha="right",
                fontsize=8, color=HARMAA)
    ax.set(xlabel="asetusten määrä (kolme arvoa kullakin)",
           ylabel="testejä", yscale="log", ylim=(3, 20_000))
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.savefig(polku)


if __name__ == "__main__":
    parit(Path(__file__).with_name("parit.png"))
