"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure
from scipy import signal

KOROSTUS = "#1F7F77"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def aliasointi(polku: Path) -> None:
    fs = 10_000.0
    t = np.linspace(0, 1.2e-3, 2_000)
    n = np.arange(13)
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(t * 1e3, np.cos(2 * np.pi * 7_000 * t), color=VAALEA,
            linewidth=1, label="7 kHz")
    ax.plot(t * 1e3, np.cos(2 * np.pi * 3_000 * t), color=KOROSTUS,
            linewidth=1.4, label="3 kHz")
    ax.plot(n / fs * 1e3, np.cos(2 * np.pi * 3_000 * n / fs), "o",
            color="black", markersize=4, label="näytteet, fs = 10 kHz")
    ax.set(xlabel="aika (ms)", ylabel="amplitudi", ylim=(-1.25, 1.25))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=3,
              frameon=False, fontsize=8)
    fig.savefig(polku)


def lovi(polku: Path) -> None:
    fs, f0, r = 500.0, 50.0, 0.98
    w0 = 2 * np.pi * f0 / fs
    nollat = np.array([np.exp(1j * w0), np.exp(-1j * w0)])
    navat = r * nollat
    b, a = signal.zpk2tf(nollat, navat, 1.0)
    b, a = b.real, a.real
    b = b * np.sum(a) / np.sum(b)
    f, H = signal.freqz(b, a, worN=4_096, fs=fs)
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2, width_ratios=[1, 1.8])
    ympyra = np.exp(1j * np.linspace(0, 2 * np.pi, 400))
    ax1.plot(ympyra.real, ympyra.imag, color=VAALEA, linewidth=1)
    ax1.plot(nollat.real, nollat.imag, "o", mfc="none", color=KOROSTUS,
             markersize=7, label="nollat")
    ax1.plot(navat.real, navat.imag, "x", color="black", markersize=7,
             label="navat")
    ax1.set(aspect="equal", xlim=(-1.3, 1.3), ylim=(-1.3, 1.3),
            xlabel="Re z", ylabel="Im z")
    ax1.axhline(0, color=VAALEA, linewidth=0.6)
    ax1.axvline(0, color=VAALEA, linewidth=0.6)
    ax1.legend(loc="lower left", frameon=False, fontsize=8)
    db = 20 * np.log10(np.maximum(np.abs(H), 1e-6))
    ax2.plot(f, db, color=KOROSTUS, linewidth=1.4)
    ax2.set(xlabel="taajuus (Hz)", ylabel="|H| (dB)", ylim=(-60, 5),
            xlim=(0, fs / 2))
    ax2.grid(alpha=0.3)
    fig.savefig(polku)


def ikkunat(polku: Path) -> None:
    N, tiheys = 64, 64
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    for nimi, vari in (("boxcar", VAALEA), ("hann", KOROSTUS),
                       ("blackman", "black")):
        w = signal.get_window(nimi, N)
        W = np.abs(np.fft.fft(w, n=N * tiheys))
        W = np.fft.fftshift(W / W.max())
        k = np.fft.fftshift(np.fft.fftfreq(N * tiheys, d=1 / N))
        ax.plot(k, 20 * np.log10(np.maximum(W, 1e-8)), color=vari,
                linewidth=1.2, label=nimi)
    ax.set(xlim=(-12, 12), ylim=(-100, 5), xlabel="taajuus (DFT-välejä)",
           ylabel="dB")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    fig.savefig(polku)


def spektrogrammi(polku: Path) -> None:
    fs = 8_000.0
    t = np.arange(int(2.0 * fs)) / fs
    x = signal.chirp(t, f0=200, t1=2.0, f1=2_000)
    x += 0.5 * np.sin(2 * np.pi * 3_000 * t) * (t > 1.0)
    w = signal.windows.hann(256, sym=False)
    stft = signal.ShortTimeFFT(w, hop=64, fs=fs, scale_to="magnitude")
    S = np.abs(stft.stft(x))
    db = 20 * np.log10(np.maximum(S / S.max(), 1e-4))
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    kuva = ax.imshow(db, origin="lower", aspect="auto", cmap="Greys",
                     extent=stft.extent(len(x)), vmin=-60, vmax=0)
    ax.set(xlabel="aika (s)", ylabel="taajuus (Hz)", xlim=(0, 2),
           ylim=(0, 4_000))
    fig.colorbar(kuva, ax=ax, label="dB")
    fig.savefig(polku)


def main(argv: list[str]) -> int:
    kohde = Path(argv[0]) if argv else Path(".")
    aliasointi(kohde / "aliasointi.png")
    lovi(kohde / "lovi.png")
    ikkunat(kohde / "ikkunat.png")
    spektrogrammi(kohde / "spektrogrammi.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
