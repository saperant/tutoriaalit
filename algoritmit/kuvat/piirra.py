"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut luetaan
esimerkkien testatuista tulosteista (esimerkit/*.odotettu).
"""

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


def kasvu(polku: Path) -> None:
    """Vertailujen määrä syötteen koon funktiona (02-kasvu.odotettu)."""
    rivit = (JUURI / "esimerkit/02-kasvu.odotettu").read_text("utf-8")
    rivit_l = rivit.splitlines()
    koot = [int(x) for x in rivit_l[0].replace("n =", "").split()[:4]]
    fig = Figure(figsize=(6.0, 3.0), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    tyylit = {"lineaarihaku": ("-", "o"), "binäärihaku": ("-", "s"),
              "lomitus": ("-", "^"), "lisäys": ("-", "D")}
    for rivi in rivit_l[1:]:
        osat = rivi.split()
        nimi = osat[-1]
        arvot = [int(x) for x in osat[:4]]
        viiva, merkki = tyylit[nimi]
        vari = KOROSTUS if nimi == "lisäys" else HARMAA
        ax.plot(koot, arvot, viiva, marker=merkki, color=vari,
                markersize=4, linewidth=1.2)
        ax.annotate(nimi, (koot[-1], arvot[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("syötteen koko n (logaritminen asteikko)")
    ax.set_ylabel("vertailuja")
    ax.set_xlim(koot[0] * 0.9, koot[-1] * 2.2)
    ax.set_xticks(koot, [str(k) for k in koot])
    ax.grid(True, which="major", color=VAALEA, linewidth=0.5)
    fig.savefig(polku / "kasvu.png", metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    kasvu(kohde)


if __name__ == "__main__":
    main()
