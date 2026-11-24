"""Piirtaa tutoriaalin kuvat. Kaytto: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tata ei ajeta testeissa. Kuvien data
tuotetaan samoin kuin lukujen testatuissa esimerkeissa.
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure
from scipy import signal

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ESIMERKIT / "fm"))
import lahetin  # noqa: E402

KOROSTUS = "#1F7F77"
HARMAA = "#5B6B70"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def kaista(polku: Path) -> None:
    """Luvun 1 tallenteen tehospektri (sama data kuin 01-spektri.py)."""
    fs = 912e3
    rng = np.random.default_rng(1)
    n = np.arange(round(0.05 * fs))
    t = n / fs

    def asema(f0: float, teho_db: float) -> np.ndarray:
        sos = signal.butter(6, 15e3, fs=fs, output="sos")
        ohjelma = signal.sosfilt(sos, rng.standard_normal(len(n)))
        ohjelma /= 3 * np.std(ohjelma)
        vaihe = 2 * np.pi * 75e3 * np.cumsum(ohjelma) / fs
        return 10 ** (teho_db / 20) * np.exp(1j * (2 * np.pi * f0 * t
                                                   + vaihe))

    x = (asema(200e3, 0.0) + asema(-250e3, -20.0)
         + 0.003 * np.exp(2j * np.pi * -60e3 * t))
    x += 0.01 * (rng.standard_normal(len(n))
                 + 1j * rng.standard_normal(len(n)))
    f, p = signal.welch(x, fs, nperseg=4096, return_onesided=False)
    f, p = np.fft.fftshift(f), np.fft.fftshift(p)
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax = fig.subplots()
    ax.plot((98e6 + f) / 1e6, 10 * np.log10(p), color=KOROSTUS, lw=0.7)
    ax.set_xlabel("taajuus (MHz)")
    ax.set_ylabel("tehotiheys (dB/Hz)")
    ax.set_xlim(97.544, 98.456)
    fig.savefig(polku)


def mpx(polku: Path) -> None:
    """MPX-signaalin spektri: summa, pilotti, erotus ja RDS."""
    m = lahetin.mpx(1.0, "TESTI FM", 0x6A01, np.random.default_rng(1))
    f, p = signal.welch(m, lahetin.FS_MPX, nperseg=8192)
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax = fig.subplots()
    ax.plot(f / 1e3, 10 * np.log10(p + 1e-20), color=KOROSTUS, lw=0.7)
    for x, teksti in ((4.5, "L+R"), (19, "pilotti"), (38, "L-R"),
                      (57, "RDS")):
        ax.annotate(teksti, (x, -20), ha="center", color=HARMAA)
    ax.set_xlim(0, 65)
    ax.set_ylim(-120, -10)
    ax.set_xlabel("taajuus (kHz)")
    ax.set_ylabel("tehotiheys (dB/Hz)")
    fig.savefig(polku)


def kynnys(polku: Path) -> None:
    """Luvun 5 kynnysmittaus (05-kynnys.py:n tulokset)."""
    rivit = (ESIMERKIT / "05-kynnys.odotettu").read_text().splitlines()[2:]
    cnr = np.array([float(r.split()[0]) for r in rivit])
    snr = np.array([float(r.split()[2]) for r in rivit])
    teoria = np.array([float(r.split()[4]) for r in rivit])
    fig = Figure(figsize=(5.0, 2.6), dpi=200, layout="constrained")
    ax = fig.subplots()
    ax.plot(cnr, teoria, color=HARMAA, lw=1, label="teoria (kynnyksen yllä)")
    ax.plot(cnr, snr, "o", color=KOROSTUS, ms=4, label="simulaatio")
    ax.set_xlabel("CNR kanavassa (dB)")
    ax.set_ylabel("lähdön SNR (dB)")
    ax.legend(frameon=False)
    fig.savefig(polku)


if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kaista(kohde / "kaista.png")
    mpx(kohde / "mpx.png")
    kynnys(kohde / "kynnys.png")
