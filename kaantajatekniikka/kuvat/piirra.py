"""Piirtää tutoriaalin kuvaajat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut luetaan
tiedostosta esimerkit/naytteet/mittaus.txt, jonka testaa.sh vertaa
kääntäjän tuottamien ohjelmien omaan käskylaskuriin. Kun mittaus
muuttuu (make -C esimerkit naytteet), kuva piirretään uudelleen
komennolla make kuvat.
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

NAYTTEET = Path(__file__).resolve().parent.parent / "esimerkit" / "naytteet"

KOROSTUS = "#6D4FA0"
TOINEN = "#B07A2A"
TUMMA = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def mittaus(polku: Path) -> None:
    """Suoritettujen käskyjen muutos -O1 -> -O2 ohjelmittain."""
    ohjelmat = []
    for rivi in (NAYTTEET / "mittaus.txt").read_text("utf-8").splitlines()[2:]:
        nimi, _, _, s1, s2 = rivi.split()[:5]
        ohjelmat.append((nimi, (int(s2) - int(s1)) * 100 / int(s1)))
    ohjelmat.sort(key=lambda o: o[1], reverse=True)
    fig = Figure(figsize=(5.2, 3.0), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    nimet = [n for n, _ in ohjelmat]
    muutokset = [m for _, m in ohjelmat]
    ax.barh(nimet, muutokset, height=0.62,
            color=[TOINEN if m > 0 else KOROSTUS for m in muutokset])
    for y, m in enumerate(muutokset):
        ax.annotate(f"{m:+.1f} %".replace(".", ",").replace("-", "−"),
                    (m, y), xytext=(3 if m > 0 else -3, 0),
                    textcoords="offset points", va="center",
                    ha="left" if m > 0 else "right", color=TUMMA, fontsize=8)
    ax.axvline(0, color=TUMMA, linewidth=0.8)
    ax.set_xlim(-40, 8)
    ax.set_xlabel("suoritettujen käskyjen muutos, -O1 → -O2 (%)")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    fig.savefig(polku / "mittaus.png", metadata=METATIEDOT)


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    mittaus(kohde)


if __name__ == "__main__":
    main()
