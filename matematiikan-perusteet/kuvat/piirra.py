"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure

KOROSTUS = "#3E7F3C"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def naytteistys(polku: Path) -> None:
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    x = np.linspace(0.0, 1.0, 101)
    ax1.plot(x, np.sin(2 * np.pi * 99 * x), color=KOROSTUS, linewidth=1.2)
    ax1.set(title="101 pistettä välillä [0, 1]", xlabel="x", ylabel="y")
    x = np.linspace(0.0, 0.1, 2000)
    ax2.plot(x, np.sin(2 * np.pi * 99 * x), color=KOROSTUS, linewidth=1.0)
    ax2.set(title="2000 pistettä välillä [0, 0,1]", xlabel="x")
    for ax in (ax1, ax2):
        ax.set_ylim(-1.2, 1.2)
    tallenna(fig, polku)


def kaanteis(polku: Path) -> None:
    fig = Figure(figsize=(3.4, 3.2), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    x = np.linspace(-2.5, 1.6, 300)
    ax.plot(x, np.exp(x), color=KOROSTUS, label="$y = e^x$")
    x = np.linspace(0.08, 5.0, 300)
    ax.plot(x, np.log(x), color=HARMAA, label="$y = \\ln x$")
    x = np.linspace(-2.5, 5.0, 2)
    ax.plot(x, x, "--", color=VAALEA, linewidth=1, label="y = x")
    ax.plot([1.0, 0.0], [0.0, 1.0], "o", color="black", markersize=3)
    ax.set(aspect="equal", xlim=(-2.5, 5.0), ylim=(-2.5, 5.0),
           xlabel="x", ylabel="y")
    ax.legend(loc="lower right", frameon=False)
    tallenna(fig, polku)


def logasteikko(polku: Path) -> None:
    kuukaudet = np.arange(0, 61)
    kayttajat = 1000 * 1.06**kuukaudet
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    for ax, asteikko in ((ax1, "linear"), (ax2, "log")):
        ax.plot(kuukaudet, kayttajat, color=KOROSTUS)
        ax.set_yscale(asteikko)
        ax.set(xlabel="kuukausi")
    ax1.set(ylabel="käyttäjiä", title="tavallinen asteikko")
    ax2.set(title="logaritminen asteikko: suora")
    ax2.grid(True, which="both", alpha=0.25)
    tallenna(fig, polku)


def yksikkoympyra(polku: Path) -> None:
    fig = Figure(figsize=(3.4, 3.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    t = np.linspace(0.0, 2 * np.pi, 400)
    ax.plot(np.cos(t), np.sin(t), color=VAALEA)
    kulma = np.pi / 6
    c, s = np.cos(kulma), np.sin(kulma)
    ax.plot([0, c], [0, s], color="black", linewidth=1)
    ax.plot([c, c], [0, s], color=KOROSTUS, linewidth=2, label="sin")
    ax.plot([0, c], [0, 0], color=HARMAA, linewidth=2, label="cos")
    kaari = np.linspace(0.0, kulma, 50)
    ax.plot(0.25 * np.cos(kaari), 0.25 * np.sin(kaari), color="black",
            linewidth=0.8)
    ax.annotate("$\\pi/6$", (0.3, 0.07))
    ax.annotate("$(\\sqrt{3}/2,\\ 1/2)$", (c, s), xytext=(c - 0.5, s + 0.15))
    ax.axhline(0, color=VAALEA, linewidth=0.6)
    ax.axvline(0, color=VAALEA, linewidth=0.6)
    ax.set(aspect="equal", xlim=(-1.2, 1.2), ylim=(-1.2, 1.2))
    ax.legend(loc="lower left", frameon=False)
    tallenna(fig, polku)


def geometria(polku: Path) -> None:
    fig = Figure(figsize=(3.6, 3.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    t = np.linspace(0.0, 2 * np.pi, 400)
    ax.plot(5 * np.cos(t), 5 * np.sin(t), color="black", linewidth=1)
    x = np.linspace(-9.0, 9.0, 2)
    for b, tyyli, nimi in ((1.0, "-", "y = x + 1"),
                           (5 * np.sqrt(2), "--", "$y = x + 5\\sqrt{2}$"),
                           (8.0, ":", "y = x + 8")):
        ax.plot(x, x + b, tyyli, color=KOROSTUS, label=nimi)
    ax.plot([-4.0, 3.0], [-3.0, 4.0], "o", color=KOROSTUS, markersize=4)
    ax.plot(x, (25 - 3 * x) / 4, color=HARMAA, label="tangentti (3, 4)")
    ax.set(aspect="equal", xlim=(-8, 8), ylim=(-8, 9), xlabel="x",
           ylabel="y")
    ax.legend(loc="lower right", frameon=False, fontsize=7)
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    for nimi, piirra in (("naytteistys", naytteistys),
                         ("kaanteis", kaanteis),
                         ("logasteikko", logasteikko),
                         ("yksikkoympyra", yksikkoympyra),
                         ("geometria", geometria)):
        piirra(kohde / f"{nimi}.png")
        print("piirretty", nimi)


if __name__ == "__main__":
    main()
