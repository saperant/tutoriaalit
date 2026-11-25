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


TOINEN = "#C2571A"


def spektri_db(x: np.ndarray, fs: float, lkm: int = 4_096
               ) -> tuple[np.ndarray, np.ndarray]:
    """Ikkunoitu amplitudispektri (dB, sinin amplitudi 1 = 0 dB)."""
    ikkuna = np.hanning(lkm)
    X = np.abs(np.fft.rfft(x[-lkm:] * ikkuna)) / (ikkuna.sum() / 2)
    return np.fft.rfftfreq(lkm, 1 / fs), 20 * np.log10(X + 1e-9)


def ensimmainen(polku: Path) -> None:
    """Luku 1: esimerkin 01-ensimmainen signaali ennen ja jalkeen."""
    siirtyma = (ESTO - PAASTO) / (FS / 2)
    lkm, beta = signal.kaiserord(60.0, siirtyma)
    lkm |= 1
    h = signal.firwin(lkm, (PAASTO + ESTO) / 2, window=("kaiser", beta),
                      fs=FS)
    rng = np.random.default_rng(1)
    n = np.arange(16_000)
    puhdas = np.sin(2 * np.pi * 440.0 / FS * n)
    hairio = 0.5 * np.sin(2 * np.pi * 2_500.0 / FS * n)
    hairio += 0.2 * rng.standard_normal(n.size)
    y = signal.lfilter(h, [1.0], puhdas + hairio)
    fig = Figure(figsize=(6.4, 3.3), dpi=200, layout="constrained")
    (a1, a2), (a3, a4) = fig.subplots(2, 2, width_ratios=[1, 1.3])
    for ax_t, ax_f, x, vari, nimi in ((a1, a2, puhdas + hairio, HARMAA,
                                       "ennen"), (a3, a4, y, KOROSTUS,
                                                  "jalkeen")):
        ax_t.plot(n[:160] / FS * 1e3, x[8_000:8_160], color=vari,
                  linewidth=0.9)
        ax_t.set(ylabel=nimi.replace("jalkeen", "jälkeen"), ylim=(-2.2, 2.2))
        f, db = spektri_db(x, FS)
        ax_f.plot(f, db, color=vari, linewidth=0.8)
        ax_f.axvspan(ESTO, FS / 2, color=VAALEA, alpha=0.3, linewidth=0)
        ax_f.set(ylim=(-110, 5), ylabel="dB")
    a3.set_xlabel("aika (ms)")
    a4.set_xlabel("taajuus (Hz); estokaista varjostettu")
    fig.savefig(polku)


def katkaisu(polku: Path) -> None:
    """Luku 3: suorakaidekatkaisu kolmella pituudella ja ikkunat."""
    fc = 0.25
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    for lkm, vari in ((21, HARMAA), (81, TOINEN), (321, KOROSTUS)):
        k = np.arange(lkm) - (lkm - 1) / 2
        f, H = signal.freqz(2 * fc * np.sinc(2 * fc * k), worN=1 << 14,
                            fs=1.0)
        ax1.plot(f, np.abs(H), color=vari, linewidth=0.9, label=f"N = {lkm}")
    ax1.set(xlim=(0.15, 0.35), xlabel="taajuus / fs", ylabel="|H|")
    ax1.set_title("suorakaidekatkaisu", fontsize=9)
    ax1.legend(frameon=False, fontsize=8)
    ikkunat: list[tuple[str | tuple[str, float], str, str]] = [
        ("boxcar", "suorakaide", HARMAA), ("hann", "Hann", TOINEN),
        ("blackman", "Blackman", KOROSTUS)]
    for ikkuna, nimi, vari in ikkunat:
        h = signal.firwin(101, fc, window=ikkuna, fs=1.0)
        f, H = signal.freqz(h, worN=1 << 14, fs=1.0)
        ax2.plot(f, 20 * np.log10(np.abs(H) + 1e-9), color=vari,
                 linewidth=0.8, label=nimi)
    ax2.set(xlim=(0.15, 0.5), ylim=(-120, 5), xlabel="taajuus / fs",
            ylabel="dB")
    ax2.set_title("ikkunat, N = 101", fontsize=9)
    ax2.legend(frameon=False, fontsize=8)
    fig.savefig(polku)


def hilbert(polku: Path) -> None:
    """Luku 4: esimerkin 04-hilbert AM-signaali ja laskettu verhokayra."""
    fs, lkm = 8_000.0, 63
    h = -signal.remez(lkm, [300.0, 3_700.0], [1.0], type="hilbert", fs=fs)
    viive = (lkm - 1) // 2
    n = np.arange(4_000)
    verho = 1.0 + 0.5 * np.sin(2 * np.pi * 20.0 / fs * n)
    x = verho * np.cos(2 * np.pi * 1_000.0 / fs * n)
    q = signal.lfilter(h, [1.0], x)
    i = np.concatenate([np.zeros(viive), x[:-viive]])
    osa = slice(400, 1_400)
    fig = Figure(figsize=(6.4, 2.2), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(n[osa] / fs * 1e3, i[osa], color=VAALEA, linewidth=0.6,
            label="signaali")
    ax.plot(n[osa] / fs * 1e3, np.abs(i + 1j * q)[osa], color=KOROSTUS,
            linewidth=1.4, label="|i + jq|")
    ax.set(xlabel="aika (ms)", ylabel="amplitudi")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=2,
              frameon=False, fontsize=8)
    fig.savefig(polku)


def monitaajuus(polku: Path) -> None:
    """Luku 9: desimointi ja interpolointi taajuustasossa."""
    fs, M = 48_000.0, 4
    n = np.arange(48_000)
    x = np.sin(2 * np.pi * 1_000.0 / fs * n) + 0.5 * np.sin(
        2 * np.pi * 7_000.0 / fs * n)
    h = signal.firwin(97, 5_000.0, window=("kaiser", 8.0), fs=fs)
    x2 = np.sin(2 * np.pi * 1_000.0 / (fs / M) * np.arange(12_000))
    tihennetty = np.zeros(x2.size * M)
    tihennetty[::M] = x2
    fig = Figure(figsize=(6.4, 3.4), dpi=200, layout="constrained")
    (a1, a2), (a3, a4) = fig.subplots(2, 2, sharey=True)
    tapaukset = (
        (a1, x[::M], fs / M, HARMAA, "desimointi ilman suodinta"),
        (a2, signal.lfilter(h, [1.0], x)[::M], fs / M, KOROSTUS,
         "suodin ensin"),
        (a3, M * tihennetty, fs, HARMAA, "nollat lisätty"),
        (a4, signal.lfilter(M * h, [1.0], tihennetty), fs, KOROSTUS,
         "suodatettu"))
    for ax, y, fy, vari, nimi in tapaukset:
        f, db = spektri_db(y, fy)
        ax.plot(f / 1e3, db, color=vari, linewidth=0.8)
        ax.set(ylim=(-130, 10))
        ax.set_title(nimi, fontsize=9)
    a1.set_ylabel("dB")
    a3.set_ylabel("dB")
    a1.annotate("7 kHz laskostuu\n5 kHz:iin", (5, -6), xytext=(3.0, -70),
                fontsize=8, arrowprops={"arrowstyle": "->", "color": HARMAA})
    a3.annotate("peilikuvat", (11, 0), xytext=(15, -60), fontsize=8,
                arrowprops={"arrowstyle": "->", "color": HARMAA})
    a3.set_xlabel("taajuus (kHz)")
    a4.set_xlabel("taajuus (kHz)")
    fig.savefig(polku)


def hurina(polku: Path) -> None:
    """Luku 10: esimerkin 10-kohinanpoisto spektrit."""
    fs = 1_000.0
    n = np.arange(20_000)
    rng = np.random.default_rng(8)
    hyoty = signal.lfilter(*signal.butter(4, [5.0, 40.0], "bandpass",
                                          fs=fs), rng.standard_normal(n.size))
    f_verkko = 50.0 + 0.5 * np.sin(2 * np.pi * 0.05 * n / fs)
    vaihe = 2 * np.pi * np.cumsum(f_verkko) / fs
    viite = np.sin(vaihe) + 0.3 * np.sin(3 * vaihe)
    d = hyoty + 0.8 * np.sin(vaihe + 1.1) + 0.2 * np.sin(3 * vaihe + 0.4)
    lkm, mu = 32, 0.01
    w, v = np.zeros(lkm), np.zeros(lkm)
    puhdistettu = np.zeros(n.size)
    for i in range(n.size):
        v = np.roll(v, 1)
        v[0] = viite[i]
        puhdistettu[i] = d[i] - w @ v
        w += mu / (1e-8 + v @ v) * puhdistettu[i] * v
    lovi = signal.filtfilt(*signal.iirnotch(50.0, 30.0, fs=fs), d)
    fig = Figure(figsize=(6.4, 2.5), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 3, sharey=True)
    for ax, y, vari, nimi in zip(
            akselit, (d, lovi, puhdistettu), (HARMAA, TOINEN, KOROSTUS),
            ("mitattu", "kiinteä lovi", "adaptiivinen"), strict=True):
        f, P = signal.welch(y[10_000:], fs=fs, nperseg=2_000)
        _, Ph = signal.welch(hyoty[10_000:], fs=fs, nperseg=2_000)
        ax.plot(f, 10 * np.log10(Ph + 1e-12), color=VAALEA, linewidth=1.2)
        ax.plot(f, 10 * np.log10(P + 1e-12), color=vari, linewidth=0.9)
        ax.set(xlim=(0, 200), ylim=(-70, 5), xlabel="taajuus (Hz)")
        ax.set_title(nimi, fontsize=9)
    akselit[0].set_ylabel("tehotiheys (dB)")
    fig.savefig(polku)


def main(argv: list[str]) -> int:
    kohde = Path(argv[0]) if argv else Path(".")
    fir(kohde / "fir.png")
    iir(kohde / "iir.png")
    lms(kohde / "lms.png")
    ensimmainen(kohde / "ensimmainen.png")
    katkaisu(kohde / "katkaisu.png")
    hilbert(kohde / "hilbert.png")
    monitaajuus(kohde / "monitaajuus.png")
    hurina(kohde / "hurina.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
