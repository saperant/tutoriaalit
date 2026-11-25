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


TOINEN = "#C2571A"


def spektrikopiot(polku: Path) -> None:
    """Luku 3: näytteistys toistaa spektrin fs:n välein."""
    B = 180.0
    f = np.linspace(-700, 700, 2801)

    def kaista(keski: float) -> np.ndarray:
        return np.maximum(0.0, 1 - np.abs(f - keski) / B)

    fig = Figure(figsize=(6.4, 2.8), dpi=200, layout="constrained")
    akselit = fig.subplots(2, 1, sharex=True)
    for ax, fs in zip(akselit, (500.0, 300.0), strict=True):
        for k in range(-3, 4):
            ax.fill_between(f, kaista(k * fs), color=KOROSTUS if k == 0
                            else VAALEA, alpha=0.75 if k == 0 else 0.6,
                            linewidth=0)
        for raja in (-fs / 2, fs / 2):
            ax.axvline(raja, color="black", linewidth=0.8, linestyle="--")
        ax.set(yticks=[], ylim=(0, 1.25), ylabel="|X(f)|")
        tila = "kopiot erillään" if fs > 2 * B else "kopiot päällekkäin"
        ax.set_title(f"fs = {fs:.0f} Hz, kaista 180 Hz: {tila}",
                     fontsize=9, loc="left")
    akselit[1].set_xlabel("taajuus (Hz); katkoviivat ±fs/2")
    fig.savefig(polku)


def rekonstruktio(polku: Path) -> None:
    """Luku 3: sinc-pulssien summa ja nollannen asteen pito."""
    fs = 500.0
    n = np.arange(-40, 60)

    def sig(t: np.ndarray) -> np.ndarray:
        return np.asarray(np.sin(2 * np.pi * 50 * t)
                          + 0.5 * np.cos(2 * np.pi * 180 * t + 0.3))

    t = np.linspace(0, 0.03, 1501)
    naytteet = sig(n / fs)
    pulssit = naytteet[:, None] * np.sinc(fs * t[None, :] - n[:, None])
    fig = Figure(figsize=(6.4, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2, sharey=True)
    nakyvat = (n >= 0) & (n <= 15)
    for p in pulssit[nakyvat]:
        ax1.plot(t * 1e3, p, color=VAALEA, linewidth=0.6)
    ax1.plot(t * 1e3, pulssit.sum(axis=0), color=KOROSTUS, linewidth=1.4)
    ax1.plot(n[nakyvat] / fs * 1e3, naytteet[nakyvat], "o", color="black",
             markersize=3)
    ax1.set(xlabel="aika (ms)", ylabel="x(t)", xlim=(0, 30))
    ax1.set_title("sinc-pulssien summa", fontsize=9)
    ax2.plot(t * 1e3, sig(t), color=VAALEA, linewidth=1.2)
    ax2.step(n[nakyvat] / fs * 1e3, naytteet[nakyvat], where="post",
             color=TOINEN, linewidth=1.2)
    ax2.plot(n[nakyvat] / fs * 1e3, naytteet[nakyvat], "o", color="black",
             markersize=3)
    ax2.set(xlabel="aika (ms)", xlim=(0, 30))
    ax2.set_title("nollannen asteen pito", fontsize=9)
    fig.savefig(polku)


def ema(polku: Path) -> None:
    """Luku 6: EMA:n askelvaste ja resonaattorin impulssivaste."""
    fs = 1_000.0
    fig = Figure(figsize=(6.4, 2.5), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    n = np.arange(200)
    for tau, vari in ((0.005, HARMAA), (0.020, KOROSTUS), (0.050, TOINEN)):
        alfa = 1 - np.exp(-1 / (fs * tau))
        y = signal.lfilter([alfa], [1.0, -(1 - alfa)], np.ones(200))
        ax1.plot(n, y, color=vari, linewidth=1.3,
                 label=f"τ = {tau * 1e3:.0f} ms")
    ax1.axhline(0.632, color=VAALEA, linewidth=0.8, linestyle=":")
    ax1.set(xlabel="aika (ms)", ylabel="askelvaste")
    ax1.legend(frameon=False, fontsize=8, loc="lower right")
    fs2, f0 = 8_000.0, 440.0
    theta = 2 * np.pi * f0 / fs2
    d = np.zeros(400)
    d[0] = 1.0
    for r, vari in ((0.99, KOROSTUS), (1.0, HARMAA), (1.003, TOINEN)):
        h = signal.lfilter([1.0], [1.0, -2 * r * np.cos(theta), r**2], d)
        ax2.plot(np.arange(400) / fs2 * 1e3, h, color=vari, linewidth=0.9,
                 label=f"r = {r}")
    ax2.set(xlabel="aika (ms)", ylabel="impulssivaste")
    ax2.legend(frameon=False, fontsize=8, loc="upper left", ncols=3,
               columnspacing=0.8, handlelength=1.2)
    fig.savefig(polku)


def navat(polku: Path) -> None:
    """Luku 7: napaparin sijainti ja sitä vastaava impulssivaste."""
    tapaukset = [(0.6, 0.3, "lähellä origoa"), (0.95, 0.3, "lähellä kehää"),
                 (1.0, 0.3, "kehällä"), (1.03, 0.3, "ulkopuolella"),
                 (0.95, 1.2, "suurempi kulma")]
    ympyra = np.exp(1j * np.linspace(0, 2 * np.pi, 400))
    d = np.zeros(60)
    d[0] = 1.0
    fig = Figure(figsize=(6.8, 2.9), dpi=200, layout="constrained")
    akselit = fig.subplots(2, 5, height_ratios=[1.15, 1])
    for (r, kulma, nimi), yla, ala in zip(tapaukset, akselit[0], akselit[1],
                                          strict=True):
        p = r * np.exp(1j * kulma)
        vari = KOROSTUS if r < 1 else (HARMAA if r == 1 else TOINEN)
        yla.plot(ympyra.real, ympyra.imag, color=VAALEA, linewidth=1)
        yla.axhline(0, color=VAALEA, linewidth=0.5)
        yla.axvline(0, color=VAALEA, linewidth=0.5)
        yla.plot([p.real, p.real], [p.imag, -p.imag], "x", color=vari,
                 markersize=6, markeredgewidth=1.5)
        yla.set(aspect="equal", xlim=(-1.25, 1.25), ylim=(-1.25, 1.25),
                xticks=[], yticks=[])
        yla.set_title(f"{nimi}\nr = {r}", fontsize=8)
        for reuna in yla.spines.values():
            reuna.set_visible(False)
        h = signal.lfilter([1.0], [1.0, -2 * r * np.cos(kulma), r**2], d)
        ala.vlines(np.arange(60), 0, h, color=vari, linewidth=0.9)
        ala.axhline(0, color=VAALEA, linewidth=0.6)
        ala.set(xlabel="n", yticks=[])
    akselit[1][0].set_ylabel("h[n]")
    fig.savefig(polku)


def butterworth(polku: Path) -> None:
    """Luku 8: esimerkin 08-freqz suotimen amplitudi, vaihe ja ryhmäviive."""
    fs = 1_000.0
    b, a = signal.butter(2, 100.0, fs=fs)
    f = np.geomspace(5, 450, 600)
    _, H = signal.freqz(b, a, worN=f, fs=fs)
    _, gd = signal.group_delay((b, a), w=f[:-1], fs=fs)
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax1, ax2, ax3 = fig.subplots(1, 3)
    ax1.semilogx(f, 20 * np.log10(np.abs(H) + 1e-12), color=KOROSTUS,
                 linewidth=1.3)
    ax1.axhline(-3.01, color=VAALEA, linewidth=0.8, linestyle=":")
    ax1.axvline(100, color=VAALEA, linewidth=0.8, linestyle=":")
    ax1.set(xlabel="taajuus (Hz)", ylabel="vahvistus (dB)", ylim=(-60, 5))
    ax2.semilogx(f, np.degrees(np.unwrap(np.angle(H))), color=KOROSTUS,
                 linewidth=1.3)
    ax2.set(xlabel="taajuus (Hz)", ylabel="vaihe (astetta)")
    ax3.semilogx(f[:-1], gd, color=KOROSTUS, linewidth=1.3)
    ax3.set(xlabel="taajuus (Hz)", ylabel="ryhmäviive (näytettä)")
    fig.savefig(polku)


def vuotaminen(polku: Path) -> None:
    """Luku 9: esimerkin 09-vuotaminen sini kokonaisin ja vajain jaksoin."""
    fs, N = 1_000.0, 100
    t = np.arange(N) / fs
    fig = Figure(figsize=(6.4, 3.4), dpi=200, layout="constrained")
    akselit = fig.subplots(2, 2)
    for (f0, vari), (ax1, ax2) in zip(((100.0, KOROSTUS), (104.9, TOINEN)),
                                      akselit, strict=True):
        x = np.cos(2 * np.pi * f0 * t)
        jatke = np.tile(x, 2)
        ax1.plot(np.arange(60, 140), jatke[60:140], color=vari,
                 linewidth=1.1)
        ax1.axvline(100, color="black", linewidth=0.8, linestyle="--")
        ax1.set(ylabel=f"{f0:g} Hz", yticks=[-1, 0, 1])
        X = np.abs(np.fft.rfft(x)) / (N / 2)
        ax2.vlines(np.fft.rfftfreq(N, 1 / fs), -80,
                   20 * np.log10(np.maximum(X, 1e-4)), color=vari,
                   linewidth=1.6)
        ax2.set(xlim=(0, 300), ylim=(-80, 5), ylabel="dB")
    akselit[0][0].set_title("jaksollinen jatke (sauma n = 100)", fontsize=9)
    akselit[0][1].set_title("DFT:n amplitudi", fontsize=9)
    akselit[1][0].set_xlabel("näyte n")
    akselit[1][1].set_xlabel("taajuus (Hz)")
    fig.savefig(polku)


def main(argv: list[str]) -> int:
    kohde = Path(argv[0]) if argv else Path(".")
    aliasointi(kohde / "aliasointi.png")
    lovi(kohde / "lovi.png")
    ikkunat(kohde / "ikkunat.png")
    spektrogrammi(kohde / "spektrogrammi.png")
    spektrikopiot(kohde / "spektrikopiot.png")
    rekonstruktio(kohde / "rekonstruktio.png")
    ema(kohde / "ema.png")
    navat(kohde / "navat.png")
    butterworth(kohde / "butterworth.png")
    vuotaminen(kohde / "vuotaminen.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
