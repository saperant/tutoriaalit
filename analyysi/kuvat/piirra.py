"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import math
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


def tangentti(polku: Path) -> None:
    """Sekantit lähestyvät tangenttia, kun h pienenee."""
    fig = Figure(figsize=(4.2, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    x = np.linspace(0.0, 2.6, 300)
    ax.plot(x, np.sin(x), color="black", linewidth=1.4, label="sin x")
    a = 1.0
    for h, vari in ((1.2, VAALEA), (0.6, HARMAA)):
        k = (math.sin(a + h) - math.sin(a)) / h
        ax.plot(x, math.sin(a) + k * (x - a), "--", color=vari,
                linewidth=1, label=f"sekantti, h = {h}".replace(".", ","))
        ax.plot([a + h], [math.sin(a + h)], "o", color=vari, markersize=3)
    ax.plot(x, math.sin(a) + math.cos(a) * (x - a), color=KOROSTUS,
            linewidth=1.4, label="tangentti")
    ax.plot([a], [math.sin(a)], "o", color="black", markersize=3)
    ax.set(xlim=(0, 2.6), ylim=(-0.1, 1.6), xlabel="x", ylabel="y")
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    tallenna(fig, polku)


def erotusvirhe(polku: Path) -> None:
    """Erotusosamäärän virhe askeleen h funktiona."""
    fig = Figure(figsize=(4.2, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    h = np.logspace(-15, -1, 200)
    eteen = np.abs((np.sin(1 + h) - np.sin(1)) / h - math.cos(1))
    keski = np.abs((np.sin(1 + h) - np.sin(1 - h)) / (2 * h) - math.cos(1))
    ax.loglog(h, eteen, color=HARMAA, linewidth=1, label="eteenpäin")
    ax.loglog(h, keski, color=KOROSTUS, linewidth=1, label="keskeinen")
    ax.set(xlabel="askel h", ylabel="virhe", ylim=(1e-12, 1))
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def newton(polku: Path) -> None:
    """Newtonin menetelmän kolme ensimmäistä askelta yhtälölle x^2 = 2."""
    fig = Figure(figsize=(4.2, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    x = np.linspace(0.8, 3.2, 300)
    ax.plot(x, x**2 - 2, color="black", linewidth=1.4)
    ax.axhline(0, color=VAALEA, linewidth=0.8)
    xn = 3.0
    for i in range(3):
        y = xn**2 - 2
        seur = xn - y / (2 * xn)
        ax.plot([xn, xn], [0, y], ":", color=HARMAA, linewidth=1)
        ax.plot([xn, seur], [y, 0], color=KOROSTUS, linewidth=1.2)
        ax.annotate(f"$x_{i}$", (xn, 0), textcoords="offset points",
                    xytext=(0, -12), ha="center", fontsize=8)
        xn = seur
    ax.set(xlim=(0.8, 3.2), ylim=(-1.5, 7.5), xlabel="x",
           ylabel="$x^2 - 2$")
    tallenna(fig, polku)


def riemann(polku: Path) -> None:
    """Vasemmat ja keskipistesummat funktiolle x^2."""
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    for ax, siirto, nimi in zip(fig.subplots(1, 2), (0.0, 0.5),
                                ("vasemmat päätepisteet",
                                 "keskipisteet"), strict=True):
        n = 8
        dx = 1 / n
        xs = np.arange(n) * dx
        ax.bar(xs, (xs + siirto * dx) ** 2, width=dx, align="edge",
               color=VAALEA, edgecolor=HARMAA, linewidth=0.6)
        x = np.linspace(0, 1, 200)
        ax.plot(x, x**2, color=KOROSTUS, linewidth=1.4)
        ax.set(title=nimi, xlabel="x", xlim=(0, 1), ylim=(0, 1.05))
    tallenna(fig, polku)


def taylor(polku: Path) -> None:
    """sin x ja sen Taylorin polynomit asteittain."""
    fig = Figure(figsize=(4.6, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    x = np.linspace(-6, 6, 400)
    ax.plot(x, np.sin(x), color="black", linewidth=1.6, label="sin x")
    p = np.zeros_like(x)
    varit = (VAALEA, HARMAA, "#7FA68A", KOROSTUS)
    for aste, vari in zip((1, 3, 5, 7), varit, strict=True):
        p = p + (-1) ** (aste // 2) * x**aste / math.factorial(aste)
        ax.plot(x, p, color=vari, linewidth=1, label=f"$P_{aste}$")
    ax.set(ylim=(-2, 2), xlim=(-6, 6), xlabel="x")
    ax.legend(frameon=False, fontsize=8, ncol=5, loc="lower center")
    tallenna(fig, polku)


def tasa_arvo(polku: Path) -> None:
    """Mäen tasa-arvokäyrät ja gradienttikenttä."""
    fig = Figure(figsize=(4.0, 3.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    x, y = np.meshgrid(np.linspace(-3, 3, 200), np.linspace(-2, 2, 200))
    h = 300 - 20 * x**2 - 40 * y**2 + 10 * x * y
    ks = ax.contour(x, y, h, levels=np.arange(-100, 301, 50),
                    colors=HARMAA, linewidths=0.7)
    ax.clabel(ks, fontsize=7, fmt="%d")
    xg, yg = np.meshgrid(np.linspace(-2.5, 2.5, 9), np.linspace(-1.6, 1.6, 7))
    gx = -40 * xg + 10 * yg
    gy = 10 * xg - 80 * yg
    ax.quiver(xg, yg, gx, gy, color=KOROSTUS, angles="xy", width=0.004)
    ax.set(aspect="equal", xlabel="x (km)", ylabel="y (km)")
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    for nimi, piirra in (("tangentti", tangentti),
                         ("erotusvirhe", erotusvirhe),
                         ("newton", newton), ("riemann", riemann),
                         ("taylor", taylor), ("tasa-arvo", tasa_arvo)):
        piirra(kohde / f"{nimi}.png")


if __name__ == "__main__":
    main()
