"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import math
import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
from matplotlib import rcParams
from matplotlib.figure import Figure
from scipy.interpolate import BarycentricInterpolator

KOROSTUS = "#9A6524"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}
Taulukko = npt.NDArray[np.float64]


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 4.2, korkeus: float = 2.8) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def derivaatta(polku: Path) -> None:
    """Erotusosamäärien virhe askeleen funktiona: V-muodot."""
    fig = uusi()
    ax = fig.add_subplot()
    h = np.logspace(-15, -0.5, 300)
    e = math.e
    eteen = np.abs((np.exp(1 + h) - e) / h - e)
    keski = np.abs((np.exp(1 + h) - np.exp(1 - h)) / (2 * h) - e)
    d1 = (np.exp(1 + h / 2) - np.exp(1 - h / 2)) / h
    rich = np.abs((4 * d1 - (np.exp(1 + h) - np.exp(1 - h)) / (2 * h)) / 3 - e)
    for y, nimi, vari in ((eteen, "eteenpäin", VAALEA),
                          (keski, "keskeinen", HARMAA),
                          (rich, "Richardson", KOROSTUS)):
        ax.loglog(h, np.maximum(y, 1e-17), color=vari, linewidth=1,
                  label=nimi)
    ax.set(xlabel="askel h", ylabel="virhe", ylim=(1e-15, 1))
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    tallenna(fig, polku)


def runge(polku: Path) -> None:
    """Interpolointipolynomit astetta 12 tasavälisillä ja Tšebyšovin
    solmuilla."""
    fig = uusi(4.6, 2.8)
    ax = fig.add_subplot()
    x = np.linspace(-1, 1, 801)

    def f(t: Taulukko) -> Taulukko:
        return 1 / (1 + 25 * t * t)

    n = 12
    tasa = np.linspace(-1, 1, n + 1)
    k = np.arange(n + 1)
    tseb = np.cos((2 * k + 1) * np.pi / (2 * n + 2))
    ax.plot(x, f(x), color="black", linewidth=1.4, label="1/(1+25x²)")
    ax.plot(x, BarycentricInterpolator(tasa, f(tasa))(x), color=HARMAA,
            linewidth=1, label="tasaväliset solmut")
    ax.plot(x, BarycentricInterpolator(tseb, f(tseb))(x), color=KOROSTUS,
            linewidth=1, label="Tšebyšovin solmut")
    ax.plot(tasa, f(tasa), "o", color=HARMAA, markersize=2.5)
    ax.plot(tseb, f(tseb), "o", color=KOROSTUS, markersize=2.5)
    ax.set(xlabel="x", ylabel="y", ylim=(-1.5, 2.0))
    ax.legend(frameon=False, fontsize=8, loc="upper center")
    tallenna(fig, polku)


def integrointi(polku: Path) -> None:
    """Integrointisääntöjen virhe funktion arvojen määrän funktiona."""
    fig = uusi()
    ax = fig.add_subplot()
    tarkka = math.e - 1
    ns = 2 ** np.arange(1, 11)
    pu, si = [], []
    for n in ns:
        x = np.linspace(0, 1, n + 1)
        y = np.exp(x)
        pu.append(abs((y[0] / 2 + y[1:-1].sum() + y[-1] / 2) / n - tarkka))
        si.append(abs((y[0] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum()
                       + y[-1]) / (3 * n) - tarkka))
    gn = np.arange(1, 9)
    ga = []
    for n in gn:
        t, w = np.polynomial.legendre.leggauss(int(n))
        ga.append(abs(0.5 * np.sum(w * np.exp(0.5 * (t + 1))) - tarkka))
    ax.loglog(ns + 1, np.maximum(pu, 1e-17), "o-", color=VAALEA,
              markersize=3, linewidth=1, label="puolisuunnikas, h²")
    ax.loglog(ns + 1, np.maximum(si, 1e-17), "o-", color=HARMAA,
              markersize=3, linewidth=1, label="Simpson, h⁴")
    ax.loglog(gn, np.maximum(ga, 1e-17), "o-", color=KOROSTUS,
              markersize=3, linewidth=1, label="Gauss")
    ax.set(xlabel="funktion arvoja", ylabel="virhe", ylim=(1e-17, 1))
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def stabiilisuus(polku: Path) -> None:
    """Stabiilisuusalueet kompleksitasossa z = h lambda."""
    fig = uusi(4.4, 3.2)
    ax = fig.add_subplot()
    x, y = np.meshgrid(np.linspace(-4, 2, 500), np.linspace(-3, 3, 500))
    z = x + 1j * y
    euler = np.abs(1 + z)
    rk4 = np.abs(1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24)
    implisiittinen = np.abs(1 / (1 - z))
    ax.contourf(x, y, (implisiittinen <= 1).astype(float), levels=[0.5, 1.5],
                colors=["#F1E7DA"])
    ax.contour(x, y, rk4, levels=[1], colors=[KOROSTUS], linewidths=1.2)
    ax.contour(x, y, euler, levels=[1], colors=[HARMAA], linewidths=1.2)
    ax.axhline(0, color=VAALEA, linewidth=0.6)
    ax.axvline(0, color=VAALEA, linewidth=0.6)
    ax.text(-1, 0.15, "Euler", color=HARMAA, ha="center", fontsize=8)
    ax.text(-2.3, 2.0, "RK4", color=KOROSTUS, fontsize=8)
    ax.text(-3.8, -2.7, "implisiittinen Euler: kaikki paitsi\n"
            "ympyrä keskipisteenä 1", fontsize=7, color=HARMAA)
    ax.set(aspect="equal", xlabel="Re hλ", ylabel="Im hλ")
    tallenna(fig, polku)


def iteraatiot(polku: Path) -> None:
    """Jäännöksen pieneneminen: Jacobi, Gauss-Seidel ja CG."""
    fig = uusi()
    ax = fig.add_subplot()
    N = 30
    A = 2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
    b = np.ones(N)
    nb = float(np.linalg.norm(b))

    def jaannos(x: Taulukko) -> float:
        return float(np.linalg.norm(b - A @ x)) / nb

    x = np.zeros(N)
    jac = []
    for _ in range(4000):
        x = x + (b - A @ x) / 2
        jac.append(jaannos(x))
    x = np.zeros(N)
    gs = []
    for _ in range(2000):
        for i in range(N):
            x[i] += (b[i] - A[i] @ x) / 2
        gs.append(jaannos(x))
    x = np.zeros(N)
    r = b.copy()
    p = r.copy()
    cg = []
    for _ in range(15):
        Ap = A @ p
        a = float(r @ r) / float(p @ Ap)
        x += a * p
        r_uusi = r - a * Ap
        p = r_uusi + float(r_uusi @ r_uusi) / float(r @ r) * p
        r = r_uusi
        cg.append(max(jaannos(x), 1e-16))
    ax.semilogy(range(1, 4001), jac, color=VAALEA, linewidth=1,
                label="Jacobi")
    ax.semilogy(range(1, 2001), gs, color=HARMAA, linewidth=1,
                label="Gauss-Seidel")
    ax.semilogy(range(1, 16), cg, "o-", color=KOROSTUS, markersize=2.5,
                linewidth=1, label="liittogradientti")
    ax.axhline(1e-8, color="black", linewidth=0.6, linestyle=":")
    ax.set(xscale="log", xlabel="kierros", ylabel="suhteellinen jäännös",
           ylim=(1e-12, 2))
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    tallenna(fig, polku)


def rosenbrock(polku: Path) -> None:
    """Gradienttimenetelmän ja Newtonin polut Rosenbrockin laaksossa."""
    fig = uusi(4.4, 3.0)
    ax = fig.add_subplot()
    x, y = np.meshgrid(np.linspace(-1.6, 1.6, 400),
                       np.linspace(-3.4, 1.7, 400))
    f = (1 - x) ** 2 + 100 * (y - x * x) ** 2
    ax.contour(x, y, np.log10(f + 1e-3), levels=15, colors=VAALEA,
               linewidths=0.6)

    def fun(v: Taulukko) -> float:
        return float((1 - v[0]) ** 2 + 100 * (v[1] - v[0] ** 2) ** 2)

    def grad(v: Taulukko) -> Taulukko:
        return np.array([-2 * (1 - v[0]) - 400 * v[0] * (v[1] - v[0] ** 2),
                         200 * (v[1] - v[0] ** 2)])

    def hess(v: Taulukko) -> Taulukko:
        return np.array([[2 - 400 * (v[1] - 3 * v[0] ** 2), -400 * v[0]],
                         [-400 * v[0], 200.0]])

    v = np.array([-1.2, 1.0])
    polku_g = [v]
    for _ in range(3000):
        g = grad(v)
        t = 1.0
        while fun(v - t * g) > fun(v) - 1e-4 * t * float(g @ g):
            t /= 2
        v = v - t * g
        polku_g.append(v)
    pg = np.array(polku_g)
    v = np.array([-1.2, 1.0])
    polku_n = [v]
    for _ in range(6):
        v = v + np.linalg.solve(hess(v), -grad(v))
        polku_n.append(v)
    pn = np.array(polku_n)
    ax.plot(pg[:, 0], pg[:, 1], color=HARMAA, linewidth=0.8,
            label="gradienttimenetelmä, 3000 askelta")
    ax.plot(pn[:, 0], pn[:, 1], "o-", color=KOROSTUS, markersize=3,
            linewidth=1, label="Newton, 6 askelta")
    ax.plot([1], [1], "*", color="black", markersize=8)
    ax.set(xlabel="x", ylabel="y")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    for nimi, piirra in (("derivaatta", derivaatta), ("runge", runge),
                         ("integrointi", integrointi),
                         ("stabiilisuus", stabiilisuus),
                         ("iteraatiot", iteraatiot),
                         ("rosenbrock", rosenbrock)):
        piirra(kohde / f"{nimi}.png")


if __name__ == "__main__":
    main()
