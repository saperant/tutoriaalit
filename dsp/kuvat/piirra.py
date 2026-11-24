"""Piirtaa tutoriaalin kuvat. Kaytto: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tata ei ajeta testeissa. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissa.
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy import signal

KOROSTUS = "#1F7F77"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False

FS, PAASTO, ESTO = 8_000.0, 1_000.0, 1_500.0


def maski(ax: Axes) -> None:
    """Vaatimusmaski: paastokaista 0,1 dB ja estokaista -60 dB."""
    ax.plot([0, PAASTO], [-0.1, -0.1], color="black", linewidth=0.8)
    ax.plot([PAASTO, PAASTO], [-0.1, -100], color="black", linewidth=0.8)
    ax.plot([ESTO, FS / 2], [-60, -60], color="black", linewidth=0.8)
    ax.plot([ESTO, ESTO], [-60, 5], color="black", linewidth=0.8)


def fir(polku: Path) -> None:
    lkm, beta = signal.kaiserord(60.0, (ESTO - PAASTO) / (FS / 2))
    kaiser = signal.firwin(lkm | 1, 1_250.0, window=("kaiser", beta),
                           fs=FS)
    dp = (10 ** (0.1 / 20) - 1) / (10 ** (0.1 / 20) + 1)
    remez = signal.remez(46, [0, PAASTO, ESTO, FS / 2], [1, 0],
                         weight=[1, dp / 1e-3], fs=FS)
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    for h, nimi, vari in ((kaiser, f"Kaiser, N = {kaiser.size}", VAALEA),
                          (remez, "Parks-McClellan, N = 46", KOROSTUS)):
        f, H = signal.freqz(h, worN=8_192, fs=FS)
        ax.plot(f, 20 * np.log10(np.maximum(np.abs(H), 1e-6)), color=vari,
                linewidth=1.3, label=nimi)
    maski(ax)
    ax.set(xlabel="taajuus (Hz)", ylabel="|H| (dB)", xlim=(0, FS / 2),
           ylim=(-100, 5))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    fig.savefig(polku)


def iir(polku: Path) -> None:
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    suotimet = (
        ("Butterworth 19", signal.butter(
            19, signal.buttord(PAASTO, ESTO, 0.1, 60, fs=FS)[1],
            output="sos", fs=FS), VAALEA),
        ("Chebyshev I 9", signal.cheby1(9, 0.1, PAASTO, output="sos",
                                        fs=FS), HARMAA),
        ("elliptinen 6", signal.ellip(6, 0.1, 60, PAASTO, output="sos",
                                      fs=FS), KOROSTUS),
    )
    for nimi, sos, vari in suotimet:
        f, H = signal.sosfreqz(sos, worN=8_192, fs=FS)
        ax.plot(f, 20 * np.log10(np.maximum(np.abs(H), 1e-6)), color=vari,
                linewidth=1.3, label=nimi)
    maski(ax)
    ax.set(xlabel="taajuus (Hz)", ylabel="|H| (dB)", xlim=(0, FS / 2),
           ylim=(-100, 5))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    fig.savefig(polku)


def lms(polku: Path) -> None:
    rng = np.random.default_rng(4)
    lkm = 16
    tuntematon = signal.firwin(lkm, 0.2)
    x = rng.standard_normal(3_000)
    d = signal.lfilter(tuntematon, [1.0], x)
    d += 0.01 * rng.standard_normal(x.size)
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    for mu, vari in ((0.002, VAALEA), (0.01, HARMAA), (0.04, KOROSTUS)):
        w, v = np.zeros(lkm), np.zeros(lkm)
        e = np.zeros(x.size)
        for n in range(x.size):
            v = np.roll(v, 1)
            v[0] = x[n]
            e[n] = d[n] - w @ v
            w += mu * e[n] * v
        tasoitettu = np.convolve(e**2, np.ones(50) / 50, mode="same")
        ax.semilogy(tasoitettu, color=vari, linewidth=1.2,
                    label=f"mu = {mu}")
    ax.axhline(1e-4, color="black", linewidth=0.8, linestyle="--")
    ax.set(xlabel="näyte n", ylabel="MSE (liukuva keskiarvo)",
           xlim=(0, x.size), ylim=(5e-5, 1))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    fig.savefig(polku)


def main(argv: list[str]) -> int:
    kohde = Path(argv[0]) if argv else Path(".")
    fir(kohde / "fir.png")
    iir(kohde / "iir.png")
    lms(kohde / "lms.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
