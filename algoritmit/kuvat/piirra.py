"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

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


def aikataulu(polku: Path) -> None:
    """Ahneiden sääntöjen vastaesimerkit aikajanalla (08-aikataulu.c)."""
    lahde = (JUURI / "esimerkit/08-aikataulu.c").read_text("utf-8")
    tuloste = (JUURI / "esimerkit/08-aikataulu.odotettu").read_text("utf-8")
    # Tulosteen taulukko: sääntö ja valittujen määrä kummassakin tapauksessa.
    luvut = {" ".join(r.split()[:-2]): [int(x) for x in r.split()[-2:]]
             for r in tuloste.splitlines()[1:5]}

    def varaukset(nimi: str) -> list[tuple[int, int]]:
        rivi = re.search(rf"Varaus {nimi}\[\] = (.*);", lahde)
        assert rivi, nimi
        return [(int(a), int(b))
                for a, b in re.findall(r"\{ (\d+), (\d+) \}", rivi.group(1))]

    def ahne(v: list[tuple[int, int]], avain) -> list[tuple[int, int]]:
        valitut: list[tuple[int, int]] = []
        for x in sorted(v, key=avain):
            if all(x[0] >= y[1] or y[0] >= x[1] for y in valitut):
                valitut.append(x)
        return valitut

    saannot = {"aikaisin alku": lambda x: x[0], "lyhin": lambda x: x[1] - x[0],
               "aikaisin loppu": lambda x: x[1]}
    tapaukset = [("pitka", 0, "aikaisin alku",
                  "Pitkä varaus alkaa ensin"),
                 ("lyhyt", 1, "lyhin", "Lyhyt varaus kahden välissä")]
    fig = Figure(figsize=(6.0, 2.3), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 2)
    for ax, (nimi, sarake, vaara, otsikko) in zip(akselit, tapaukset):
        v = varaukset(nimi)
        for rivi, saanto in enumerate((vaara, "aikaisin loppu")):
            valitut = ahne(v, saannot[saanto])
            # Kuvan valinnat ovat samat kuin testatun ohjelman tulosteessa.
            assert len(valitut) == luvut[saanto][sarake], (nimi, saanto)
            for i, (a, b) in enumerate(sorted(v)):
                mukana = (a, b) in valitut
                y = -rivi * (len(v) + 1.5) - i
                ax.barh(y, b - a, left=a, height=0.7,
                        color=KOROSTUS if mukana and saanto == vaara
                        else HARMAA if mukana else "white",
                        edgecolor=HARMAA, linewidth=0.8)
            ax.text(-0.3, -rivi * (len(v) + 1.5) - (len(v) - 1) / 2,
                    f"{saanto}:\n{len(valitut)} varausta", ha="right",
                    va="center", fontsize=7)
        ax.set_title(otsikko, fontsize=8)
        ax.set_yticks([])
        ax.set_xlabel("aika", fontsize=8)
        ax.spines["left"].set_visible(False)
        ax.tick_params(labelsize=7)
    fig.savefig(polku / "aikataulu.png", metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    kasvu(kohde)
    aikataulu(kohde)


if __name__ == "__main__":
    main()
