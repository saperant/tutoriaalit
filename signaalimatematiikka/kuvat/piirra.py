"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoilla parametreilla kuin lukujen testatuissa esimerkeissä.
"""

import cmath
import math
import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure

KOROSTUS = "#1F7F77"
TOINEN = "#C2571A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def taso(ax: Axes, raja: float) -> None:
    """Kompleksitason akselit origon kautta."""
    ax.axhline(0, color=VAALEA, linewidth=0.8)
    ax.axvline(0, color=VAALEA, linewidth=0.8)
    ax.set(aspect="equal", xlim=(-raja, raja), ylim=(-raja, raja),
           xlabel="Re", ylabel="Im")


def nuoli(ax: Axes, alku: complex, loppu: complex, vari: str,
          paksuus: float = 1.4) -> None:
    ax.annotate("", xy=(loppu.real, loppu.imag),
                xytext=(alku.real, alku.imag),
                arrowprops={"arrowstyle": "-|>", "color": vari,
                            "linewidth": paksuus, "shrinkA": 0,
                            "shrinkB": 0})


def taajuudet(polku: Path) -> None:
    """Luku 1: esimerkin 01-taajuudet signaali ajassa ja taajuudessa."""
    fs = 1000
    t = np.arange(fs) / fs
    x = 1.5 * np.sin(2 * np.pi * 50 * t) + 0.5 * np.cos(2 * np.pi * 120 * t)
    f = np.fft.rfftfreq(len(x), d=1 / fs)
    amplitudi = 2 * np.abs(np.fft.rfft(x)) / len(x)
    fig = Figure(figsize=(6.4, 2.3), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    ax1.plot(t[:101] * 1e3, x[:101], color=KOROSTUS, linewidth=1.2)
    ax1.set(xlabel="aika (ms)", ylabel="x(t)", title="aikataso")
    ax2.vlines(f[:201], 0, amplitudi[:201], color=KOROSTUS, linewidth=2)
    ax2.set(xlabel="taajuus (Hz)", ylabel="amplitudi", title="taajuustaso",
            xlim=(0, 200), ylim=(0, 1.7))
    for fk, a in ((50, 1.5), (120, 0.5)):
        ax2.annotate(f"{fk} Hz", (fk, a), textcoords="offset points",
                     xytext=(6, -2), fontsize=8)
    fig.savefig(polku)


def kierto(polku: Path) -> None:
    """Luku 2: esimerkin 02-kierto neliö ennen ja jälkeen kertolaskun."""
    nelio = np.array([1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j, 1 + 1j])
    kerroin = cmath.rect(2, math.pi / 6)
    uusi = kerroin * nelio
    fig = Figure(figsize=(3.6, 3.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    taso(ax, 3.2)
    ax.plot(nelio.real, nelio.imag, color=HARMAA, linewidth=1.2,
            label="alkuperäinen")
    ax.plot(uusi.real, uusi.imag, color=KOROSTUS, linewidth=1.6,
            label="kerrottu luvulla 2∠30°")
    nuoli(ax, 0, nelio[0], HARMAA, 1.0)
    nuoli(ax, 0, uusi[0], KOROSTUS, 1.0)
    ax.plot(nelio[0].real, nelio[0].imag, "o", color=HARMAA, markersize=4)
    ax.plot(uusi[0].real, uusi[0].imag, "o", color=KOROSTUS, markersize=4)
    ax.annotate("1 + i", (1, 1), textcoords="offset points", xytext=(5, -10),
                fontsize=8)
    ax.annotate("0,732 + 2,732i", (uusi[0].real, uusi[0].imag),
                textcoords="offset points", xytext=(5, 3), fontsize=8)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=2,
              frameon=False, fontsize=8)
    fig.savefig(polku)


def euler(polku: Path) -> None:
    """Luku 3: (1 + i theta/n)^n askelina ja ykkösen kahdeksannet juuret."""
    theta = 2.0
    ympyra = np.exp(1j * np.linspace(0, 2 * np.pi, 400))
    fig = Figure(figsize=(6.4, 3.1), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    taso(ax1, 1.45)
    ax1.plot(ympyra.real, ympyra.imag, color=VAALEA, linewidth=1)
    for n, vari in ((4, TOINEN), (16, HARMAA), (64, KOROSTUS)):
        z = (1 + 1j * theta / n) ** np.arange(n + 1)
        ax1.plot(z.real, z.imag, "-", color=vari, linewidth=1.1,
                 marker="o", markersize=2.2 if n > 4 else 3.5,
                 label=f"n = {n}")
    tarkka = cmath.exp(1j * theta)
    ax1.plot(tarkka.real, tarkka.imag, "x", color="black", markersize=7,
             label="$e^{2i}$")
    ax1.legend(loc="lower left", frameon=False, fontsize=8)
    ax1.set_title("$(1 + i\\theta/n)^k$, $\\theta = 2$", fontsize=9)
    taso(ax2, 1.45)
    ax2.plot(ympyra.real, ympyra.imag, color=VAALEA, linewidth=1)
    juuret = np.exp(2j * np.pi * np.arange(8) / 8)
    for k, w in enumerate(juuret):
        nuoli(ax2, 0, complex(w), KOROSTUS if k == 1 else HARMAA, 1.0)
        ax2.annotate(f"$w^{k}$", (1.22 * w.real, 1.22 * w.imag),
                     ha="center", va="center", fontsize=8)
    ax2.set_title("ykkösen 8. juuret, $w = e^{2\\pi i/8}$", fontsize=9)
    fig.savefig(polku)


def osoitin(polku: Path) -> None:
    """Luku 4: esimerkin 04-osoitin pyörivä osoitin ja osoitinsumma."""
    A, f, phi = 2.0, 250.0, math.pi / 3
    X = cmath.rect(A, phi)
    t = np.linspace(0, 0.008, 801)
    fig = Figure(figsize=(6.8, 2.6), dpi=200, layout="constrained")
    ax1, ax2, ax3 = fig.subplots(1, 3, width_ratios=[1, 1.25, 1])
    ympyra = A * np.exp(1j * np.linspace(0, 2 * np.pi, 400))
    taso(ax1, 2.5)
    ax1.plot(ympyra.real, ympyra.imag, color=VAALEA, linewidth=1)
    nuoli(ax1, 0, X, KOROSTUS)
    ax1.plot([X.real, X.real], [X.imag, 0], ":", color=HARMAA, linewidth=1)
    ax1.plot(X.real, 0, "o", color=TOINEN, markersize=4)
    ax1.set_title("osoitin X = 2∠60°, t = 0", fontsize=9)
    x = np.real(X * np.exp(2j * np.pi * f * t))
    ax2.plot(t * 1e3, x, color=KOROSTUS, linewidth=1.3)
    ax2.plot(0, X.real, "o", color=TOINEN, markersize=4)
    ax2.axhline(0, color=VAALEA, linewidth=0.8)
    ax2.set(xlabel="aika (ms)", ylabel="Re", ylim=(-2.5, 2.5))
    ax2.set_title("reaaliosa ajan funktiona", fontsize=9)
    osat = [cmath.rect(1.0, 0.0), cmath.rect(1.5, -math.pi / 2),
            cmath.rect(0.8, 2.5)]
    taso(ax3, 1.9)
    alku = 0j
    for z, vari in zip(osat, (HARMAA, HARMAA, HARMAA), strict=True):
        nuoli(ax3, alku, alku + z, vari, 1.0)
        alku += z
    nuoli(ax3, 0, alku, KOROSTUS)
    ax3.annotate("summa", (alku.real / 2, alku.imag / 2),
                 textcoords="offset points", xytext=(-30, -6), fontsize=8,
                 color=KOROSTUS)
    ax3.set_title("kolmen osoittimen summa", fontsize=9)
    fig.savefig(polku)


def huojunta(polku: Path) -> None:
    """Luku 4: esimerkin 04-interferenssi huojunta ja verhokäyrä."""
    f1, f2 = 440.0, 444.0
    t = np.linspace(0, 0.6, 30_001)
    x = np.cos(2 * np.pi * f1 * t) + np.cos(2 * np.pi * f2 * t)
    verho = 2 * np.abs(np.cos(np.pi * (f2 - f1) * t))
    fig = Figure(figsize=(6.4, 2.2), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(t, x, color=VAALEA, linewidth=0.5, label="440 Hz + 444 Hz")
    ax.plot(t, verho, color=KOROSTUS, linewidth=1.4,
            label="verhokäyrä 2|cos(π·4t)|")
    ax.plot(t, -verho, color=KOROSTUS, linewidth=1.4)
    ax.set(xlabel="aika (s)", ylabel="x(t)", xlim=(0, 0.6))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=2,
              frameon=False, fontsize=8)
    fig.savefig(polku)


def kantti_osasumma(t: np.ndarray, termeja: int) -> np.ndarray:
    k = np.arange(1, 2 * termeja, 2)[:, np.newaxis]
    return np.asarray(np.sum(4 / (np.pi * k) * np.sin(k * t), axis=0))


def osasummat(polku: Path) -> None:
    """Luku 6: kanttiaallon osasummat ja Gibbsin ylitys hypyn vieressä."""
    t = np.linspace(-0.4, 2 * np.pi + 0.4, 4001)
    kantti = np.where(np.mod(t, 2 * np.pi) < np.pi, 1.0, -1.0)
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2, width_ratios=[1.5, 1])
    ax1.plot(t, kantti, color=VAALEA, linewidth=1.2, label="kanttiaalto")
    for n, vari, lw in ((1, HARMAA, 0.9), (3, TOINEN, 0.9),
                        (25, KOROSTUS, 1.1)):
        ax1.plot(t, kantti_osasumma(t, n), color=vari, linewidth=lw,
                 label=f"{n} termi" + ("ä" if n > 1 else ""))
    ax1.set(xlabel="t", ylabel="osasumma", ylim=(-1.45, 1.45))
    ax1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=4,
               frameon=False, fontsize=7, columnspacing=1.0)
    lahi = np.linspace(-0.05, 0.5, 4001)
    ax2.axhline(1.0, color=VAALEA, linewidth=1.2)
    ax2.axhline(1.179, color=VAALEA, linewidth=0.8, linestyle=":")
    for n, vari in ((5, HARMAA), (20, TOINEN), (100, KOROSTUS)):
        ax2.plot(lahi, kantti_osasumma(lahi, n), color=vari, linewidth=1.0,
                 label=f"{n}")
    ax2.set(xlabel="t (hypyn vieressä)", ylim=(0.6, 1.25), xlim=(-0.02, 0.5))
    ax2.annotate("huippu 1,179", (0.33, 1.185), fontsize=8, color=HARMAA)
    ax2.legend(title="termejä", loc="lower right", frameon=False,
               fontsize=8, title_fontsize=8)
    fig.savefig(polku)


def kertoimet(polku: Path) -> None:
    """Luku 6: kertoimien pieneneminen kantti-, saha- ja kolmioaallolla."""
    k = np.arange(1, 64)
    pariton = k % 2 == 1
    fig = Figure(figsize=(4.6, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.loglog(k[pariton], 4 / (np.pi * k[pariton]), "o", color=KOROSTUS,
              markersize=3.5, label="kantti: 4/(πk)")
    ax.loglog(k, 2 / (np.pi * k), "s", color=HARMAA, markersize=2.8,
              label="saha: 2/(πk)")
    ax.loglog(k[pariton], 8 / (np.pi * k[pariton]) ** 2, "^", color=TOINEN,
              markersize=3.5, label="kolmio: 8/(πk)²")
    ax.set(xlabel="harmoninen k", ylabel="kertoimen itseisarvo")
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(polku)


def parit(polku: Path) -> None:
    """Luku 7: rect–sinc ja kapea ja leveä Gaussin pulssi spektreineen."""
    t = np.linspace(-3, 3, 1201)
    f = np.linspace(-4, 4, 1201)
    fig = Figure(figsize=(6.4, 3.6), dpi=200, layout="constrained")
    (a1, a2), (a3, a4) = fig.subplots(2, 2)
    a1.plot(t, np.where(np.abs(t) <= 0.5, 1.0, 0.0), color=KOROSTUS,
            linewidth=1.3)
    a1.set(ylabel="x(t)", title="kanttipulssi rect t")
    a2.plot(f, np.sinc(f), color=KOROSTUS, linewidth=1.3)
    a2.axhline(0, color=VAALEA, linewidth=0.8)
    a2.set(ylabel="X(f)", title="sinc f")
    for a, vari, nimi in ((2.0, TOINEN, "kapea: $e^{-\\pi (2t)^2}$"),
                          (0.5, KOROSTUS, "leveä: $e^{-\\pi (t/2)^2}$")):
        a3.plot(t, np.exp(-np.pi * (a * t) ** 2), color=vari, linewidth=1.3,
                label=nimi)
        a4.plot(f, np.exp(-np.pi * (f / a) ** 2) / a, color=vari,
                linewidth=1.3)
    a3.set(xlabel="aika t", ylabel="x(t)")
    a3.legend(frameon=False, fontsize=7, loc="upper right")
    a4.set(xlabel="taajuus f", ylabel="X(f)")
    fig.savefig(polku)


def keskiarvo(polku: Path) -> None:
    """Luku 8: esimerkin 08-keskiarvo signaali ja liukuvat keskiarvot."""
    rng = np.random.default_rng(2026)
    n = np.arange(20000)
    puhdas = np.sin(2 * np.pi * n / 200)
    mitattu = puhdas + rng.uniform(-1.0, 1.0, size=n.size)
    fig = Figure(figsize=(6.4, 3.4), dpi=200, layout="constrained")
    akselit = fig.subplots(2, 2, sharex=True, sharey=True)
    for ax, M in zip(akselit.flat, (1, 4, 16, 64), strict=True):
        y = np.convolve(mitattu, np.ones(M) / M, mode="same")
        ax.plot(n[:600], y[:600], color=KOROSTUS if M > 1 else HARMAA,
                linewidth=0.8)
        ax.plot(n[:600], puhdas[:600], color="black", linewidth=0.7,
                linestyle="--")
        ax.set_title("mitattu" if M == 1 else f"ikkuna M = {M}", fontsize=9)
    for ax in akselit[1]:
        ax.set_xlabel("näyte n")
    fig.savefig(polku)


def taajuusvaste(polku: Path) -> None:
    """Luku 9: liukuvan keskiarvon taajuusvaste (esimerkki 09-taajuusvaste)."""
    N = 4096
    f = np.fft.rfftfreq(N)
    fig = Figure(figsize=(6.4, 2.5), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    for M, vari in ((4, HARMAA), (8, KOROSTUS), (16, TOINEN)):
        H = np.abs(np.fft.rfft(np.ones(M) / M, n=N))
        ax1.plot(f, H, color=vari, linewidth=1.2, label=f"M = {M}")
        ax2.plot(f, 20 * np.log10(np.maximum(H, 1e-4)), color=vari,
                 linewidth=1.2)
    ax1.set(xlabel="taajuus (jaksoa/näyte)", ylabel="|H(f)|")
    ax1.legend(frameon=False, fontsize=8)
    ax2.set(xlabel="taajuus (jaksoa/näyte)", ylabel="|H(f)| (dB)",
            ylim=(-50, 3))
    fig.savefig(polku)


KUVAT = {
    "taajuudet": taajuudet, "kierto": kierto, "euler": euler,
    "osoitin": osoitin, "huojunta": huojunta, "osasummat": osasummat,
    "kertoimet": kertoimet, "parit": parit, "keskiarvo": keskiarvo,
    "taajuusvaste": taajuusvaste,
}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"kirjoitettu {kohde / nimi}.png")
