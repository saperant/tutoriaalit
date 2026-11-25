"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
samoilla funktioilla kuin lukujen testatuissa esimerkeissä.
"""

import contextlib
import importlib.util
import io
import os
import statistics
import sys
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path
from types import ModuleType

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))

import historia  # noqa: E402
import organisaatio  # noqa: E402

KOROSTUS = "#1D6F80"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def lataa(nimi: str) -> ModuleType:
    """Lataa numeroidun esimerkin moduulina ja vaimentaa sen tulosteen."""
    spec = importlib.util.spec_from_file_location(
        nimi.replace("-", "_"), ESIMERKIT / f"{nimi}.py")
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(moduuli)
    return moduuli


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 4.4, korkeus: float = 2.7) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def yhteismuutokset(polku: Path) -> None:
    """Yhdessä muuttuneiden osien matriisi esimerkkihistoriasta."""
    lahto = Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            historia.luo_repositorio()
            loki = historia.lue_loki()
        finally:
            os.chdir(lahto)
    osat = organisaatio.OSAT
    yhdessa = Counter(pari for m in loki
                      for pari in combinations(sorted(m.osat), 2))
    matriisi = [[yhdessa[tuple(sorted((a, b)))] if a != b else 0
                 for b in osat] for a in osat]
    fig = uusi(3.1, 2.6)
    ax = fig.add_subplot()
    kuva = ax.imshow(matriisi, cmap="GnBu")
    ax.set_xticks(range(len(osat)), osat, rotation=90, fontsize=6)
    ax.set_yticks(range(len(osat)), osat, fontsize=6)
    for raja in (2.5, 5.5, 8.5):
        ax.axhline(raja, color="white", lw=1.5)
        ax.axvline(raja, color="white", lw=1.5)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    palkki = fig.colorbar(kuva, ax=ax, shrink=0.8)
    palkki.set_label("yhteisiä muutoksia", fontsize=7)
    palkki.ax.tick_params(labelsize=7)
    tallenna(fig, polku)


def luovutukset(polku: Path) -> None:
    """Läpimenoajan keskiarvo viidellä tavalla järjestää sama työ."""
    m = lataa("03-luovutukset")
    saapumiset, vaiheet, virrat = m.tyot()
    nimet, arvot, varit = [], [], []
    for ottovali, nimi in ((0, "erikoistiimit,\nheti"),
                           (1, "erikoistiimit,\npäivittäin"),
                           (5, "erikoistiimit,\nviikoittain")):
        valmiit = m.erikoistiimit(saapumiset, vaiheet, ottovali)
        nimet.append(nimi)
        arvot.append(statistics.fmean(
            v - s for s, v in zip(saapumiset, valmiit, strict=True)))
        varit.append(TOINEN)
    for hidastus in (1.0, 1.15):
        valmiit = m.ominaisuustiimit(saapumiset, vaiheet, virrat, hidastus)
        nimet.append(f"ominaisuus-\ntiimit, × {hidastus:.2f}"
                     .replace(".", ","))
        arvot.append(statistics.fmean(
            v - s for s, v in zip(saapumiset, valmiit, strict=True)))
        varit.append(KOROSTUS)
    fig = uusi(3.9, 1.8)
    ax = fig.add_subplot()
    palkit = ax.bar(nimet, arvot, color=varit, width=0.6)
    ax.bar_label(palkit, labels=[f"{a:.1f}".replace(".", ",")
                                 for a in arvot], fontsize=7)
    tyoaika = statistics.fmean(sum(v) for v in vaiheet)
    ax.axhline(tyoaika, color=HARMAA, lw=0.8, ls="--")
    ax.set_xlim(-0.5, 5.1)
    ax.text(4.4, tyoaika + 0.3, "pelkkä työ", color=HARMAA, fontsize=6.5,
            ha="left")
    ax.set_ylabel("läpimenoaika (päivää)", fontsize=7.5)
    ax.set_yticks(range(0, 13, 4))
    ax.tick_params(axis="x", labelsize=6, length=0)
    ax.tick_params(axis="y", labelsize=7.5)
    tallenna(fig, polku)


def viestinta(polku: Path) -> None:
    """Viestintäpolut väen kasvaessa: yksi ryhmä ja tiimit."""
    m = lataa("05-viestinta")
    vaki = [8, 16, 32, 64, 128]
    fig = uusi(3.8, 2.3)
    ax = fig.add_subplot()
    ax.plot(vaki, [m.parit(n) for n in vaki], color=TOINEN, marker="o",
            ms=3, label="yksi ryhmä")
    ax.plot(vaki, [m.tiimeina(n, 3)[0] for n in vaki], color=KOROSTUS,
            marker="o", ms=3, label="tiimien sisällä")
    ax.plot(vaki[1:], [m.tiimeina(n, 3)[1] for n in vaki[1:]],
            color=HARMAA, marker="o", ms=3, label="tiimien välillä")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(vaki, [str(n) for n in vaki])
    ax.set_xlabel("väkeä")
    ax.set_ylabel("polkuja tai suhteita")
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


KUVAT = {"yhteismuutokset": yhteismuutokset, "luovutukset": luovutukset,
         "viestinta": viestinta}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    for nimi, piirtaja in KUVAT.items():
        piirtaja(kohde / f"{nimi}.png")
        print(f"{nimi}.png")
