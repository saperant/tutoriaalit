"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat ovat versionhallinnassa, joten tätä ei ajeta testeissä. Luvut
luetaan esimerkkien testatuista tulosteista (esimerkit/*.odotettu).
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

# Algoritmin nimi -> (väri, viivatyyli, merkki)
TYYLIT = {
    "FIFO": (KOROSTUS, "-", "o"),
    "LRU": (HARMAA, "-", "s"),
    "Clock": (HARMAA, "--", "^"),
    "OPT": ("#222222", ":", "D"),
}


def sivunkorvaus(polku: Path) -> None:
    """Sivuvirheet kehysmäärän funktiona (06-sivunkorvaus.odotettu)."""
    teksti = (JUURI / "esimerkit/06-sivunkorvaus.odotettu").read_text(
        "utf-8")
    lohkot = [b.splitlines() for b in teksti.split("\n\n")[:3]]
    fig = Figure(figsize=(6.4, 2.5), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 3, sharey=True)
    for ax, lohko in zip(akselit, lohkot):
        otsikko = lohko[0].split(":")[0]
        nimet = lohko[1].split()[1:]
        taulukko = [[int(x) for x in rivi.split()] for rivi in lohko[2:]]
        kehykset = [r[0] for r in taulukko]
        for i, nimi in enumerate(nimet):
            vari, viiva, merkki = TYYLIT[nimi]
            ax.plot(kehykset, [r[i + 1] for r in taulukko], viiva,
                    marker=merkki, color=vari, markersize=3.5,
                    linewidth=1.1, label=nimi)
        ax.set_title(otsikko, fontsize=9)
        ax.set_xlabel("kehyksiä")
        ax.set_xticks(kehykset)
        ax.grid(True, color=VAALEA, linewidth=0.5)
    akselit[0].set_ylabel("sivuvirheitä")
    akselit[0].legend(frameon=False, fontsize=8)
    fig.savefig(polku / "sivunkorvaus.png", metadata={"Software": None})


def levyjono(polku: Path) -> None:
    """Lukupään reitti neljällä algoritmilla (11-levyjono.odotettu)."""
    rivit = (JUURI / "esimerkit/11-levyjono.odotettu").read_text(
        "utf-8").splitlines()
    alku = int(rivit[0].split()[2].rstrip(","))
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 4, sharey=True)
    for ax, rivi in zip(akselit, rivit[1:]):
        alkuosa, jono = rivi.split(":")
        nimi, _, liike = alkuosa.split()
        urat = [alku] + [int(x) for x in jono.split()]
        if nimi == "SCAN":
            # SCAN käy levyn reunassa ennen kääntymistä.
            huippu = urat.index(max(urat))
            urat.insert(huippu + 1, 199)
        ax.plot(range(len(urat)), urat, "-o", color=KOROSTUS,
                markersize=3, linewidth=1.1)
        ax.set_title(f"{nimi}: liike {liike}", fontsize=9)
        ax.set_xlabel("palvelujärjestys")
        ax.set_xticks([])
        ax.set_ylim(0, 205)
        ax.grid(True, axis="y", color=VAALEA, linewidth=0.5)
    akselit[0].set_ylabel("ura")
    fig.savefig(polku / "levyjono.png", metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    sivunkorvaus(kohde)
    levyjono(kohde)


if __name__ == "__main__":
    main()
