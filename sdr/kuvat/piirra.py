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


TOINEN = "#C2571A"
VAALEA = "#B8C4C8"


def spektri_db(z: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Kaksipuolinen ikkunoitu spektri (dB, kompleksinen sini 1 = 0 dB)."""
    w = np.hanning(len(z))
    Z = np.fft.fftshift(np.fft.fft(z * w)) / w.sum()
    f = np.fft.fftshift(np.fft.fftfreq(len(z), 1 / fs))
    return f, 20 * np.log10(np.abs(Z) + 1e-9)


def epaideaalisuudet(polku: Path) -> None:
    """Luku 3: tasakomponentti, IQ-epatasapaino ja AGC (esimerkit 03-*)."""
    fs, n = 912e3, 1 << 14
    k = np.arange(n)
    fig = Figure(figsize=(6.8, 4.4), dpi=200, layout="constrained")
    (a1, a2), (a3, a4) = fig.subplots(2, 2)
    rng = np.random.default_rng(6)
    x = (0.1 * np.exp(2j * np.pi * 30e3 * k / fs) + (0.02 - 0.012j)
         + 1e-3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n)))
    pitka = np.tile(x, 8)
    y = signal.lfilter([1.0, -1.0], [1.0, -0.999], pitka)[-n:]
    for z, vari, nimi in ((x, HARMAA, "ennen"), (y, KOROSTUS, "DC-esto")):
        f, db = spektri_db(z, fs)
        a1.plot(f / 1e3, db, color=vari, linewidth=0.8, label=nimi)
    a1.set(xlim=(-60, 60), ylim=(-110, 0), ylabel="dB")
    a1.set_title("tasakomponentti", fontsize=9)
    a1.legend(frameon=False, fontsize=8, loc="upper left")
    rng = np.random.default_rng(7)
    binni = round(50e3 / fs * n)
    ihanne = np.exp(2j * np.pi * binni / n * k) + 1e-3 * (
        rng.standard_normal(n) + 1j * rng.standard_normal(n))
    eps, phi = 0.05, np.radians(3.0)
    i, q = ihanne.real, ihanne.imag
    z = i + 1j * (1 + eps) * (q * np.cos(phi) + i * np.sin(phi))
    qk = z.imag - np.mean(z.real * z.imag) / np.mean(z.real**2) * z.real
    qk *= np.sqrt(np.mean(z.real**2) / np.mean(qk**2))
    for zz, vari, nimi in ((z, HARMAA, "5 %, 3°"),
                           (z.real + 1j * qk, KOROSTUS, "korjattu")):
        f, db = spektri_db(zz, fs)
        a2.plot(f / 1e3, db, color=vari, linewidth=0.8, label=nimi)
    a2.annotate("peilikuva", (-50, -30), xytext=(-20, -12), fontsize=8,
                arrowprops={"arrowstyle": "->", "color": HARMAA})
    a2.set(xlim=(-100, 100), ylim=(-110, 5))
    a2.set_title("IQ-epätasapaino", fontsize=9)
    a2.legend(frameon=False, fontsize=8, loc="upper right")
    fs2 = 48e3
    tasot_db = np.repeat([-40.0, -10.0, -25.0], round(0.1 * fs2))
    kk = np.arange(len(tasot_db))
    x2 = 10 ** (tasot_db / 20) * np.exp(2j * np.pi * 1e3 * kk / fs2)
    a_isku = 1 - np.exp(-1 / (1e-3 * fs2))
    a_pal = 1 - np.exp(-1 / (50e-3 * fs2))
    taso = -6.0
    vahvistus = np.empty(len(kk))
    lahto = np.empty(len(kk))
    for j, nayte in enumerate(x2):
        hetki = 20 * np.log10(abs(nayte) + 1e-12)
        taso += (a_isku if hetki > taso else a_pal) * (hetki - taso)
        vahvistus[j] = -6.0 - taso
        lahto[j] = hetki + vahvistus[j]
    t = kk / fs2 * 1e3
    a3.plot(t, tasot_db, color=HARMAA, linewidth=1.0, label="tulo")
    a3.plot(t, lahto, color=KOROSTUS, linewidth=1.2, label="lähtö")
    a3.set(xlabel="aika (ms)", ylabel="taso (dBFS)", ylim=(-45, 30))
    a3.set_title("vahvistuksen säätö", fontsize=9)
    a3.legend(frameon=False, fontsize=8, loc="upper right", ncols=2)
    a4.plot(t, vahvistus, color=TOINEN, linewidth=1.2)
    a4.set(xlabel="aika (ms)", ylabel="vahvistus (dB)")
    a4.set_title("AGC:n vahvistus", fontsize=9)
    a1.set_xlabel("taajuus (kHz)")
    a2.set_xlabel("taajuus (kHz)")
    fig.savefig(polku)


def paketit(polku_vesi: Path, polku_ilmaisin: Path) -> None:
    """Luku 7: esimerkin paketti/main.py tallenne vesiputouksena ja
    FM-ilmaisimen lahto ensimmaisen paketin alusta."""
    fm_lahetin = sys.modules.pop("lahetin")
    sys.path.insert(0, str(ESIMERKIT / "paketti"))
    import lahetin as lh
    import vastaanotin as va
    sys.path.pop(0)
    sys.modules["lahetin"] = fm_lahetin

    rng = np.random.default_rng(433)
    viestit = [
        (0.004, b"T=21.5C H=40%", 18.0, +3_100.0),
        (0.020, b"T=21.6C H=41%", 11.0, -1_800.0),
        (0.036, b"T=21.6C H=41%", 18.0, +3_100.0),
        (0.0365, b"OVI AUKI", 16.0, -9_000.0),
        (0.052, b"PARISTO OK", 7.0, +500.0),
    ]
    x = lh.tallenne(viestit, kesto=0.07, keskitaajuus=-150e3, rng=rng)
    f, t, S = signal.spectrogram(x, fs=lh.FS, nperseg=256, noverlap=128,
                                 return_onesided=False)
    jarj = np.argsort(f)
    fig = Figure(figsize=(6.4, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    db = 10 * np.log10(S[jarj] + 1e-15)
    kuva = ax.pcolormesh(t * 1e3, f[jarj] / 1e3, db, cmap="viridis",
                         vmin=db.max() - 35, vmax=db.max(), rasterized=True)
    ax.set(xlabel="aika (ms)", ylabel="taajuus (kHz)", ylim=(-260, -40))
    fig.colorbar(kuva, ax=ax, label="dB", pad=0.01)
    fig.savefig(polku_vesi)

    z = va.kanava(x, -150e3)
    taaj = va.taajuus(z)
    fs = lh.FS / va.DESIMOINTI
    alku = va.hae(taaj)[0]
    pohja = va.mallipohja()
    osa = slice(alku - 40, alku + len(pohja) + 16 * va.SPS)
    tt = (np.arange(osa.start, osa.stop) - alku) / fs * 1e3
    fig = Figure(figsize=(6.4, 2.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(tt, taaj[osa], color=KOROSTUS, linewidth=0.9,
            label="ilmaisimen lähtö")
    ax.plot(np.arange(len(pohja)) / fs * 1e3, pohja, color=HARMAA,
            linewidth=0.8, linestyle="--", label="mallipohja")
    raja = len(lh.ALKUOSA) * 8 * va.SPS / fs * 1e3
    loppu = len(pohja) / fs * 1e3
    ax.axvspan(raja, loppu, color=VAALEA, alpha=0.4, linewidth=0)
    ax.axhline(0, color=VAALEA, linewidth=0.6)
    ax.text(raja / 2, 2.0, "alkuosa 1010…", ha="center", fontsize=8)
    ax.text((raja + loppu) / 2, 2.0, "tahdistus", ha="center", fontsize=8)
    ax.text(loppu + 0.02, 2.0, "data", fontsize=8)
    ax.set(xlabel="aika paketin alusta (ms)", ylim=(-2.6, 2.6),
           ylabel="taajuus / poikkeama")
    ax.legend(frameon=False, fontsize=8, loc="lower right", ncols=2)
    fig.savefig(polku_ilmaisin)


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


def gnuradio(polku: Path) -> None:
    """Luvun 9 vertailu: sama tallenne omalla vastaanottimella ja
    GNU Radion lohkokaaviolla (samat ohjelmat kuin esimerkkien testissa).
    Vaatii GNU Radion; ajetaan gnuradio/gr-python-kaynnistimella."""
    import subprocess
    import tempfile

    gr = ESIMERKIT / "gnuradio"
    sys.path.insert(0, str(gr / "oma"))
    import vertaa
    sys.path.pop(0)
    with tempfile.TemporaryDirectory() as tyo:
        subprocess.run([sys.executable, str(gr / "oma" / "valmistele.py")],
                       cwd=tyo, check=True)
        subprocess.run([str(gr / "gr-python"),
                        str(gr / "lohkokaavio" / "fm_mono.py"),
                        "asema.cu8", "gr.f32", "taso.f32"], cwd=tyo,
                       check=True, capture_output=True)
        oma = vertaa.lue(str(Path(tyo) / "viite.f32"))
        kaavio = vertaa.lue(str(Path(tyo) / "gr.f32"))
    viive, _ = vertaa.kohdista(oma, kaavio)
    fs = 48_000.0
    fig = Figure(figsize=(7.2, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2, width_ratios=[1.25, 1.0])
    for x, vari, nimi, lw in ((oma, HARMAA, "oma vastaanotin", 2.2),
                              (kaavio, KOROSTUS, "GNU Radio", 0.9)):
        f, p = signal.welch(x[len(x) // 4:], fs, nperseg=4096,
                            scaling="spectrum")
        ax1.plot(f / 1e3, 10 * np.log10(p), color=vari, lw=lw, label=nimi)
    ax1.set_xlim(0, 24)
    ax1.set_ylim(-125, -5)
    ax1.set_xlabel("taajuus (kHz)")
    ax1.set_ylabel("taso (dBFS)")
    ax1.annotate("testiäänet 700 Hz\nja 1,9 kHz", (2.0, -40), (3.6, -62),
                 fontsize=8,
                 arrowprops={"arrowstyle": "-", "color": HARMAA, "lw": 0.6})
    ax1.annotate("pilotin jäännös\n19 kHz", (19.0, -100), (20.4, -72),
                 fontsize=8, ha="center",
                 arrowprops={"arrowstyle": "-", "color": HARMAA, "lw": 0.6})
    ax1.legend(frameon=False, loc="upper right")
    alku = len(oma) // 2
    n = np.arange(240)
    ax2.plot(1e3 * n / fs, oma[alku + n], color=HARMAA, lw=2.2,
             label="oma")
    ax2.plot(1e3 * n / fs, kaavio[alku + viive + n], color=KOROSTUS,
             lw=0.9, label=f"GNU Radio, siirretty {-viive} näytettä")
    ax2.set_xlabel("aika (ms)")
    ax2.set_ylabel("ääni")
    ax2.set_ylim(-0.5, 0.62)
    ax2.legend(frameon=False, loc="upper right", fontsize=8)
    fig.savefig(polku)


if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kaista(kohde / "kaista.png")
    mpx(kohde / "mpx.png")
    kynnys(kohde / "kynnys.png")
    epaideaalisuudet(kohde / "epaideaalisuudet.png")
    paketit(kohde / "vesiputous.png", kohde / "ilmaisin.png")
    gnuradio(kohde / "gnuradio.png")
