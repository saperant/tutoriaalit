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
from scipy import signal
from scipy.integrate import solve_ivp

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


def suuntakentta(polku: Path) -> None:
    """Logistisen yhtälön suuntakenttä ja muutama ratkaisu."""
    fig = Figure(figsize=(4.4, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    r, K = 0.5, 1000.0
    t, n = np.meshgrid(np.linspace(0, 16, 22), np.linspace(0, 1400, 16))
    dn = r * n * (1 - n / K)
    # Janat piirretään akselien mittakaavassa yhtä pitkiksi.
    pituus = np.hypot(1 / 16, dn / 1400) / 0.012
    dx, dy = 1 / pituus, dn / pituus
    for x0, y0, ex, ey in zip(t.ravel(), n.ravel(), dx.ravel(), dy.ravel(),
                              strict=True):
        ax.plot([x0 - ex, x0 + ex], [y0 - ey, y0 + ey], color=VAALEA,
                linewidth=0.9)
    aika = np.linspace(0, 16, 300)
    for n0 in (20, 200, 600, 1400):
        ratk = K * n0 * np.exp(r * aika) / (K + n0 * (np.exp(r * aika) - 1))
        ax.plot(aika, ratk, color=KOROSTUS, linewidth=1.2)
    ax.axhline(K, color=HARMAA, linewidth=0.8, linestyle="--")
    ax.axhline(0, color=HARMAA, linewidth=0.8, linestyle="--")
    ax.text(16.2, K, "K", va="center", color=HARMAA)
    ax.set(xlim=(0, 16), ylim=(-30, 1450), xlabel="aika t (vuotta)",
           ylabel="koko N")
    tallenna(fig, polku)


def vaimennus(polku: Path) -> None:
    """Vaimennetun värähtelijän kolme tapausta."""
    fig = Figure(figsize=(4.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    t = np.linspace(0, 8, 400)
    a = math.sqrt(15) / 2
    ali = np.exp(-t / 2) * (np.cos(a * t) + np.sin(a * t) / math.sqrt(15))
    kriittinen = (1 + 2 * t) * np.exp(-2 * t)
    yli = (4 * np.exp(-t) - np.exp(-4 * t)) / 3
    ax.plot(t, ali, color=KOROSTUS, linewidth=1.2, label="c = 1, alivaimennettu")
    ax.plot(t, kriittinen, color="black", linewidth=1.2,
            label="c = 4, kriittinen")
    ax.plot(t, yli, color=HARMAA, linewidth=1.2, linestyle="--",
            label="c = 5, ylivaimennettu")
    ax.axhline(0, color=VAALEA, linewidth=0.8)
    ax.set(xlabel="aika t (s)", ylabel="poikkeama y")
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def resonanssi(polku: Path) -> None:
    """Pakotetun värähtelyn amplitudi eri vaimennuksilla."""
    fig = Figure(figsize=(4.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    w = np.linspace(0.01, 5, 500)
    for zeta, vari in ((0.05, KOROSTUS), (0.1, "black"), (0.3, HARMAA),
                       (0.7, VAALEA)):
        amp = 1 / np.sqrt((4 - w**2) ** 2 + (4 * zeta * w) ** 2)
        ax.plot(w, amp, color=vari, linewidth=1.2,
                label=f"zeta = {zeta}".replace(".", ","))
    ax.set(yscale="log", xlabel="kulmataajuus w (rad/s)",
           ylabel="amplitudi", ylim=(0.02, 6))
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def vaihetaso(polku: Path) -> None:
    """Vaimennetun heilurin vaihetaso: spiraali alhaalla, satula ylhäällä."""
    fig = Figure(figsize=(4.6, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    th, om = np.meshgrid(np.linspace(-4, 10, 60), np.linspace(-3.5, 3.5, 40))
    ax.streamplot(th, om, om, -np.sin(th) - 0.5 * om, color=VAALEA,
                  density=1.1, linewidth=0.6, arrowsize=0.6)

    def f(_t: float, z: np.ndarray) -> np.ndarray:
        return np.array([z[1], -math.sin(z[0]) - 0.5 * z[1]])

    for alku in ((0.0, 3.4), (0.0, 2.4), (2.0, 0.0)):
        r = solve_ivp(f, (0, 25), alku, max_step=0.02)
        ax.plot(r.y[0], r.y[1], color=KOROSTUS, linewidth=1.1)
    for x in (0, 2 * math.pi):
        ax.plot([x], [0], "o", color="black", markersize=4)
    for x in (-math.pi, math.pi, 3 * math.pi):
        ax.plot([x], [0], "o", color="white", markeredgecolor="black",
                markersize=4)
    ax.set(xlim=(-4, 10), ylim=(-3.5, 3.5), xlabel="kulma theta (rad)",
           ylabel="kulmanopeus omega")
    tallenna(fig, polku)


def askelvaste(polku: Path) -> None:
    """RLC-alipäästön askelvaste ja navat."""
    fig = Figure(figsize=(5.2, 2.4), dpi=200, layout="constrained")
    ax, ax2 = fig.subplots(1, 2, width_ratios=[2, 1])
    w0 = 1e4
    aika = np.linspace(0, 3e-3, 1500)
    for zeta, vari in ((0.1, KOROSTUS), (0.5, "black"), (1.0, HARMAA)):
        jarj = signal.lti([w0**2], [1.0, 2 * zeta * w0, w0**2])
        _, y = signal.step(jarj, T=aika)
        ax.plot(aika * 1000, y, color=vari, linewidth=1.1,
                label=f"zeta = {zeta}".replace(".", ","))
        navat = np.roots([1.0, 2 * zeta * w0, w0**2])
        ax2.plot(navat.real / 1000, navat.imag / 1000, "x", color=vari,
                 markersize=6)
    ax.set(xlabel="aika (ms)", ylabel="u_C / U")
    ax.legend(frameon=False, fontsize=8)
    ax2.axvline(0, color=VAALEA, linewidth=0.8)
    ax2.axhline(0, color=VAALEA, linewidth=0.8)
    ax2.set(xlabel="Re s (1/ms)", ylabel="Im s (1/ms)", xlim=(-12, 2),
            ylim=(-11, 11))
    tallenna(fig, polku)


def jaykka(polku: Path) -> None:
    """Askeleen pituus jäykässä yhtälössä: RK45 vastaan Radau."""
    fig = Figure(figsize=(4.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()

    def f(t: float, y: np.ndarray) -> np.ndarray:
        tulos: np.ndarray = -1000.0 * (y - np.cos(t))
        return tulos

    for menetelma, vari in (("RK45", HARMAA), ("Radau", KOROSTUS)):
        r = solve_ivp(f, (0, 10), [0.0], method=menetelma, rtol=1e-6,
                      atol=1e-9)
        ax.semilogy(r.t[1:], np.diff(r.t), color=vari, linewidth=1.1,
                    label=f"{menetelma}: {len(r.t) - 1} askelta")
    ax.axhline(2.8e-3, color=VAALEA, linewidth=0.8, linestyle="--")
    ax.set(xlabel="aika t", ylabel="askel h")
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def rajasykli(polku: Path) -> None:
    """Van der Polin oskillaattorin radat kiertyvät rajasykliin."""
    fig = Figure(figsize=(4.4, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()

    def f(_t: float, z: np.ndarray) -> np.ndarray:
        return np.array([z[1], (1 - z[0] ** 2) * z[1] - z[0]])

    for alku, vari in (((0.05, 0.0), KOROSTUS), ((3.5, 2.5), HARMAA)):
        r = solve_ivp(f, (0, 40), alku, max_step=0.01)
        ax.plot(r.y[0], r.y[1], color=vari, linewidth=1.0)
    ax.plot([0], [0], "o", color="white", markeredgecolor="black",
            markersize=4)
    ax.set(xlabel="x", ylabel="x'", xlim=(-3, 4), ylim=(-3.2, 3.2))
    tallenna(fig, polku)


KUVAT = {
    "suuntakentta": suuntakentta,
    "vaimennus": vaimennus,
    "resonanssi": resonanssi,
    "vaihetaso": vaihetaso,
    "askelvaste": askelvaste,
    "jaykka": jaykka,
    "rajasykli": rajasykli,
}

if __name__ == "__main__":
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"{nimi}.png")
