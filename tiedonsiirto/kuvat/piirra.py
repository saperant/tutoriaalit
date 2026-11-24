"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure
from scipy.special import erfc

KOROSTUS = "#1F7F77"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rng = np.random.default_rng(1)


def Q(x: np.ndarray) -> np.ndarray:
    tulos: np.ndarray = 0.5 * erfc(x / np.sqrt(2))
    return tulos


def qam16() -> np.ndarray:
    tasot = np.array([-3, -1, 1, 3]) / np.sqrt(10)
    return (tasot[:, None] + 1j * tasot[None, :]).ravel()


def rrc(beta: float, sps: int, janne: int) -> np.ndarray:
    t = np.arange(-janne * sps // 2, janne * sps // 2 + 1) / sps
    h = np.empty_like(t)
    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif np.isclose(abs(ti), 1 / (4 * beta)):
            h[i] = beta / np.sqrt(2) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta))
                    + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / (
                np.pi * ti * (1 - (4 * beta * ti) ** 2))
    tulos: np.ndarray = h / np.sqrt(np.sum(h**2))
    return tulos


def konstellaatio(polku: Path) -> None:
    p = qam16()
    s = p[rng.integers(0, 16, 3_000)]
    kohina = (rng.standard_normal(len(s)) + 1j * rng.standard_normal(len(s)))
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 3)
    otsikot = ("Es/N0 = 20 dB", "Es/N0 = 14 dB", "20 dB, vaihevirhe 10 astetta")
    for ax, otsikko, sigma, kierto in zip(
            akselit, otsikot, (0.07, 0.14, 0.07), (0.0, 0.0, 10.0),
            strict=True):
        r = s * np.exp(1j * np.radians(kierto)) + sigma * kohina
        ax.plot(r.real, r.imag, ".", markersize=1.2, color=KOROSTUS,
                alpha=0.5)
        ax.plot(p.real, p.imag, "+", color="black", markersize=6)
        for raja in (-2 / np.sqrt(10), 0, 2 / np.sqrt(10)):
            ax.axvline(raja, color=VAALEA, linewidth=0.6)
            ax.axhline(raja, color=VAALEA, linewidth=0.6)
        ax.set(aspect="equal", xlim=(-1.4, 1.4), ylim=(-1.4, 1.4),
               title=otsikko, xticks=[], yticks=[])
        ax.title.set_fontsize(8)
    fig.savefig(polku)


def silma(polku: Path) -> None:
    sps, janne = 16, 12
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, beta in zip(akselit, (0.2, 0.8), strict=True):
        h = rrc(beta, sps, janne)
        s = 1.0 - 2 * rng.integers(0, 2, 400)
        x = np.zeros(len(s) * sps)
        x[::sps] = s
        y = np.convolve(np.convolve(x, h), h)
        viive = len(h) - 1
        t = np.arange(-sps, sps + 1) / sps
        for k in range(30, 330):
            alku = viive + k * sps - sps
            ax.plot(t, y[alku: alku + 2 * sps + 1], color=KOROSTUS,
                    linewidth=0.4, alpha=0.3)
        ax.axvline(0, color=HARMAA, linewidth=0.6, linestyle=":")
        ax.set(title=f"beta = {beta}", xlabel="aika (T)", xlim=(-1, 1))
        ax.title.set_fontsize(8)
    akselit[0].set_ylabel("sovitetun suotimen lähtö")
    fig.savefig(polku)


def ber(polku: Path) -> None:
    EbN0_dB = np.linspace(0, 20, 201)
    g = 10 ** (EbN0_dB / 10)
    fig = Figure(figsize=(6.4, 3.0), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    kayrat = [("BPSK, QPSK", Q(np.sqrt(2 * g)), KOROSTUS, "-")]
    for M, vari in ((16, "black"), (64, HARMAA)):
        k = np.log2(M)
        kayrat.append((f"{M}-QAM", 4 / k * (1 - 1 / np.sqrt(M))
                       * Q(np.sqrt(3 * k * g / (M - 1))), vari, "-"))
    mu = np.sqrt(g / (1 + g))
    kayrat.append(("BPSK, Rayleigh", (1 - mu) / 2, KOROSTUS, "--"))
    for nimi, arvo, vari, viiva in kayrat:
        ax.semilogy(EbN0_dB, arvo, viiva, color=vari, linewidth=1.3,
                    label=nimi)
    ax.set(xlabel="Eb/N0 (dB)", ylabel="bittivirhesuhde", ylim=(1e-7, 0.5),
           xlim=(0, 20))
    ax.grid(alpha=0.3, which="both")
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(polku)


if __name__ == "__main__":
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    konstellaatio(kohde / "konstellaatio.png")
    silma(kohde / "silma.png")
    ber(kohde / "ber.png")
