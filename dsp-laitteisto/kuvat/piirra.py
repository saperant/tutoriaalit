"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Käyrät lasketaan
samoilla bittitarkoilla malleilla (esimerkit/malli) ja analyyseillä
(esimerkit/analyysit), joihin testit vertaavat RTL:n ulostulon bitti
bitiltä. Mallin ulostulo on siis sama kuin RTL-simulaation.
"""

import math
import random
import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from scipy.signal import windows

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "esimerkit"))

from analyysit import cic as cic_analyysi
from analyysit import cordic_tarkkuus, nco_piikit
from malli import kertoimet as k
from malli.cordic import ROTAATIO, esikierto, iteraatio, nco
from malli.kiintea import kierra
from malli.suotimet import biquad, cic, fir, sos

KOROSTUS = "#B04848"          # alueen Laitteistosuunnittelu väri
TOINEN = "#2F6F8F"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
HAALEA = "#EEF1F2"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 6.4, korkeus: float = 2.6) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def pilkku(*akselit: Axes, x: bool = True, y: bool = False) -> None:
    """Desimaalipilkku akselien lukuihin."""
    muoto = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")
                          .replace("-", "−"))
    for ax in akselit:
        if x:
            ax.xaxis.set_major_formatter(muoto)
        if y:
            ax.yaxis.set_major_formatter(muoto)


# --- Luku 4: IIR ---------------------------------------------------------

def iir_askel(polku: Path) -> None:
    """Testin askel: saturoiva ja kiertävä kavennus (BUGI_KIERTO)."""
    askel = [32767] * 144
    oikea = sos(askel, k.SOS, k.IIR_MURTO, k.IIR_BITIT)
    kierto = sos(askel, k.SOS, k.IIR_MURTO, k.IIR_BITIT, saturaatio=False)
    assert kierto[14] == -31674 and oikea[14] == 32767   # testin tuloste
    fig = uusi(6.4, 2.5)
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, y, nimi in ((akselit[0], oikea, "saturoiva kavennus"),
                        (akselit[1], kierto, "kiertävä kavennus")):
        ax.axhline(32767, color=VAALEA, linewidth=0.8)
        ax.axhline(-32768, color=VAALEA, linewidth=0.8)
        ax.plot(range(len(y)), y, color=KOROSTUS, linewidth=0.9,
                marker="o", markersize=1.5)
        ax.set_title(nimi, fontsize=8)
        ax.set_xlabel("näyte")
        ax.grid(alpha=0.3)
    akselit[0].set_ylabel("ulostulo (koodi)")
    akselit[0].set_ylim(-52000, 37000)
    akselit[0].set_yticks([-32768, 0, 32767])
    akselit[1].annotate("näyte 14: −31674", (14, -31674), (30, -46000),
                        fontsize=7, color=MUSTE,
                        arrowprops={"arrowstyle": "-", "color": HARMAA,
                                    "linewidth": 0.6})
    tallenna(fig, polku)


def iir_kuollut(polku: Path) -> None:
    """Ensimmäisen lohkon askelvaste tasolle 10000 ja sen loppuarvo."""
    y = biquad([10000] * 400, k.SOS[0], k.IIR_MURTO, k.IIR_BITIT)
    fig = uusi(6.4, 2.3)
    vasen, oikea = fig.subplots(1, 2)
    vasen.plot(range(120), y[:120], color=KOROSTUS, linewidth=1.2)
    vasen.axhline(10000, color=VAALEA, linewidth=0.8, zorder=0)
    vasen.set(xlabel="näyte", ylabel="ulostulo (koodi)")
    vasen.grid(alpha=0.3)
    oikea.plot(range(60, 400), y[60:], color=KOROSTUS, linewidth=1.2)
    oikea.axhline(10000, color=VAALEA, linewidth=0.8, zorder=0)
    oikea.set(xlabel="näyte", ylim=(9994, 10012))
    oikea.set_title("suurennos: tavoite 10000", fontsize=8)
    oikea.text(395, y[-1] + 0.6, f"{y[-1]}", ha="right", fontsize=7.5,
               color=KOROSTUS)
    oikea.grid(alpha=0.3)
    oikea.ticklabel_format(useOffset=False)
    tallenna(fig, polku)


# --- Luku 5: CORDIC ------------------------------------------------------

def cordic_kierto(polku: Path) -> None:
    """Vektorin kierto iteraatio kerrallaan ja tarkkuus kierrosten
    funktiona (sama mittaus kuin analyysissä cordic_tarkkuus)."""
    fig = uusi(6.4, 2.9)
    vasen, oikea = fig.subplots(1, 2, width_ratios=[1, 1.1])
    kulmat = k.cordic_kulmat(8)
    x0 = 1 << 15
    z = round(50 / 360 * (1 << 16))                 # kierto 50 astetta
    x, y, zz = esikierto(ROTAATIO, x0, 0, z)
    x0 <<= 2                                        # sisäinen muoto Q3.17
    pisteet = [(x, y)]
    for i in range(8):
        x, y, zz = iteraatio(ROTAATIO, i, x, y, zz, kulmat[i])
        pisteet.append((x, y))
    t = np.linspace(0, math.pi / 2, 100)
    for sade, tyyli in ((1.0, "-"), (k.cordic_vahvistus(8), "--")):
        vasen.plot(sade * np.cos(t), sade * np.sin(t), tyyli, color=VAALEA,
                   linewidth=0.8)
    for i, (px, py) in enumerate(pisteet):
        vasen.plot([0, px / x0], [0, py / x0], color=KOROSTUS,
                   linewidth=0.6, alpha=0.35 + 0.08 * i)
        if i < 5:
            vasen.text(px / x0 * 1.05, py / x0 * 1.05, str(i), fontsize=7,
                       ha="center", va="center")
    vasen.plot([p[0] / x0 for p in pisteet], [p[1] / x0 for p in pisteet],
               "o", color=KOROSTUS, markersize=2.5)
    vasen.plot([0, math.cos(math.radians(50)) * 1.9],
               [0, math.sin(math.radians(50)) * 1.9], ":", color=MUSTE,
               linewidth=0.8)
    vasen.text(1.28, 1.72, "50°", fontsize=7.5)
    vasen.set_aspect("equal")
    vasen.set(xlim=(0, 1.9), ylim=(0, 1.9), xlabel="x", ylabel="y")
    vasen.set_title("vektori kierrosten 0–8 jälkeen", fontsize=8)
    pilkku(vasen, y=True)

    rng = random.Random(1)
    koe = [rng.randint(-(1 << 15), (1 << 15) - 1) for _ in range(2000)]
    kierrokset = list(range(2, 17))
    bitit = [15 - math.log2(cordic_tarkkuus.suurin_virhe(n, koe))
             for n in kierrokset]
    oikea.plot(kierrokset, [n - 1 for n in kierrokset], color=VAALEA,
               linewidth=1.2, label="bitti kierrosta kohden")
    oikea.plot(kierrokset, bitit, "o-", color=KOROSTUS, markersize=3,
               linewidth=1.1, label="mitattu (20-bittinen datapolku)")
    oikea.set(xlabel="kierrokset", ylabel="tarkkuus (bittiä)",
              xticks=range(2, 17, 2))
    oikea.grid(alpha=0.3)
    oikea.legend(frameon=False, fontsize=7.5, loc="upper left")
    tallenna(fig, polku)


# --- Luku 6: NCO ---------------------------------------------------------

def spektri(y: list[int]) -> tuple[np.ndarray, np.ndarray]:
    n = len(y)
    s = np.abs(np.fft.rfft(np.array(y, dtype=float)
                           * windows.blackmanharris(n)))
    return np.fft.rfftfreq(n), 20 * np.log10(s / s.max() + 1e-12)


def nco_spektri(polku: Path) -> None:
    """NCO:n spektri kahdella taajuussanalla (oletusleveydet)."""
    n = 1 << 13
    fig = uusi(6.4, 2.5)
    akselit = fig.subplots(1, 2, sharey=True)
    tapaukset = (
        (1 << (k.NCO_VAIHE - 6), "taajuussana $2^{18}$: $f_s/64$"),
        (0x0A3D71, "taajuussana 0x0A3D71: noin 0,04 $f_s$"))
    for ax, (sana, nimi) in zip(akselit, tapaukset, strict=True):
        f, db = spektri(nco(sana, n))
        ax.plot(f, db, color=KOROSTUS, linewidth=0.5)
        ax.set_title(nimi, fontsize=8)
        ax.set(xlabel="taajuus / $f_s$", xlim=(0, 0.5), ylim=(-130, 5))
        ax.grid(alpha=0.3)
        pilkku(ax)
    akselit[0].set_ylabel("taso (dB kantoaallosta)")
    tallenna(fig, polku)


def nco_sfdr(polku: Path) -> None:
    """SFDR vaihebittien funktiona (sama mittaus kuin analyysissä)."""
    osoitteet = list(range(4, 11))
    mitattu = [nco_piikit.sfdr(o, 16, 0x0A3D71) for o in osoitteet]
    bitit = [o + 2 for o in osoitteet]
    fig = uusi(4.6, 2.4)
    ax = fig.add_subplot()
    ax.plot(bitit, [6.02 * b for b in bitit], color=VAALEA, linewidth=1.3,
            label="6 dB vaihebittiä kohden")
    ax.plot(bitit, mitattu, "o-", color=KOROSTUS, markersize=3.5,
            linewidth=1.1, label="mitattu mallista")
    ax.set(xlabel="vaihebitit (taulukon osoite + 2)", ylabel="SFDR (dB)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


# --- Luku 7: CIC ---------------------------------------------------------

def cic_vaste(polku: Path) -> None:
    """CIC:n vaste sisääntulon taajuuksilla ja päästökaistan taipuma
    kolmen kertoimen kompensaattorin kanssa ja ilman."""
    n, r = k.CIC_ASTEET, k.CIC_DESIMOINTI
    fig = uusi(6.4, 2.6)
    vasen, oikea = fig.subplots(1, 2, width_ratios=[1.35, 1])
    f = np.linspace(1e-6, 0.5, 2000)
    db = [20 * math.log10(max(cic_analyysi.vaste(x, n, r), 1e-9)) for x in f]
    vasen.plot(f * r, db, color=KOROSTUS, linewidth=1.2)
    kaista = 0.25                      # hyötykaista ulostulon fs:n osina
    vasen.axvspan(0, kaista, color=HAALEA, zorder=0)
    for m in range(1, r // 2 + 1):
        vasen.axvspan(m - kaista, min(m + kaista, r / 2), color="#F0DADA",
                      zorder=0)
    vasen.set(xlabel="taajuus / ulostulon $f_s$", ylabel="vaste (dB)",
              ylim=(-120, 5), xlim=(0, r / 2))
    vasen.grid(alpha=0.3)
    pilkku(vasen)

    h = cic_analyysi.kompensaattori(n, r)
    fp = np.linspace(1e-6, 0.3, 300)
    ilman = [20 * math.log10(cic_analyysi.vaste(x / r, n, r)) for x in fp]
    kanssa = [a + 20 * math.log10(cic_analyysi.cfir_vaste(h, x))
              for a, x in zip(ilman, fp, strict=True)]
    oikea.axhline(0, color=VAALEA, linewidth=0.8)
    oikea.plot(fp, ilman, color=KOROSTUS, linewidth=1.2, label="CIC")
    oikea.plot(fp, kanssa, color=TOINEN, linewidth=1.2,
               label="CIC ja kompensaattori")
    oikea.set(xlabel="taajuus / ulostulon $f_s$", ylim=(-4, 1))
    oikea.set_title("päästökaistan taipuma (dB)", fontsize=8)
    oikea.grid(alpha=0.3)
    oikea.legend(frameon=False, fontsize=7.5, loc="lower left")
    pilkku(oikea)
    tallenna(fig, polku)


def cic_integraattorit(polku: Path) -> None:
    """Integraattorien arvot täydellä askeleella: välitulokset kiertävät,
    ulostulo on silti oikea. Laskenta on sama kuin mallin cic()."""
    n, r, b = k.CIC_ASTEET, k.CIC_DESIMOINTI, k.CIC_SISAINEN
    askel = [2047] * 96
    integ = [0] * n
    kammat = [0] * n
    jaljet: list[list[int]] = [[] for _ in range(n)]
    ulos: list[int] = []
    for i, nayte in enumerate(askel):
        tulot = [nayte, *integ[:-1]]
        integ = [kierra(a + t, b) for a, t in zip(integ, tulot, strict=True)]
        for jalki, arvo in zip(jaljet, integ, strict=True):
            jalki.append(arvo)
        arvo = integ[-1]
        if i % r == r - 1:
            for j in range(n):
                arvo, kammat[j] = kierra(arvo - kammat[j], b), arvo
            ulos.append(arvo >> (b - k.CIC_ULOS))
    assert ulos == cic(askel, n, r, b, k.CIC_ULOS)
    fig = uusi(6.4, 2.6)
    vasen, oikea = fig.subplots(1, 2, width_ratios=[1.5, 1])
    raja = 1 << (b - 1)
    for jalki, vari, nimi in zip(jaljet, (VAALEA, TOINEN, KOROSTUS),
                                 ("1. integraattori", "2. integraattori",
                                  "3. integraattori"), strict=True):
        vasen.plot(range(len(askel)), [a / raja for a in jalki],
                   color=vari, linewidth=1.0, label=nimi)
    vasen.axhline(1, color=HARMAA, linewidth=0.6, linestyle=":")
    vasen.axhline(-1, color=HARMAA, linewidth=0.6, linestyle=":")
    vasen.set(xlabel="sisääntulon näyte", ylabel="arvo / $2^{20}$",
              yticks=[-1, 0, 1])
    vasen.legend(frameon=False, fontsize=7, loc="lower center",
                 bbox_to_anchor=(0.5, 1.0), ncols=3)
    vasen.grid(alpha=0.3)
    oikea.plot(range(len(ulos)), ulos, "o-", color=KOROSTUS, markersize=3,
               linewidth=1.1)
    oikea.axhline(2047 * 512 >> 5, color=VAALEA, linewidth=0.8, zorder=0)
    oikea.set(xlabel="ulostulon näyte", xticks=range(0, 12, 2))
    oikea.set_title("ulostulo: oikea askelvaste", fontsize=8)
    oikea.grid(alpha=0.3)
    tallenna(fig, polku)


# --- Luku 9: taajuusvaste mitattuna -------------------------------------

def mitattu_vaste(polku: Path) -> None:
    """FIR-suotimen vaste kertoimista ja mitattuna bittitarkan mallin
    ulostulosta (sama jono kuin RTL:n ulostulo)."""
    h = np.array(k.FIR, dtype=float) / (1 << k.KERROIN_MURTO)
    f = np.linspace(0, 0.5, 600)
    kaava = np.abs([np.sum(h * np.exp(-2j * math.pi * x * np.arange(len(h))))
                    for x in f])
    taajuudet = np.arange(1, 32) / 64
    mitattu = []
    n = 512
    siirto = k.KERROIN_MURTO
    for ft in taajuudet:
        x = [round(1800 * math.sin(2 * math.pi * ft * i)) for i in range(n)]
        y = fir(x, k.FIR, siirto, k.DATA_BITIT)
        osa_x = np.array(x[64:], dtype=float)
        osa_y = np.array(y[64:], dtype=float)
        mitattu.append(float(np.sqrt(np.mean(osa_y**2) / np.mean(osa_x**2))))
    fig = uusi(5.6, 2.6)
    ax = fig.add_subplot()
    ax.plot(f, 20 * np.log10(kaava + 1e-9), color=VAALEA, linewidth=1.6,
            label="kertoimista laskettu")
    ax.plot(taajuudet, 20 * np.log10(np.array(mitattu) + 1e-9), "o",
            color=KOROSTUS, markersize=3,
            label="mitattu ulostulosta (malli = RTL)")
    ax.set(xlabel="taajuus / $f_s$", ylabel="vahvistus (dB)", xlim=(0, 0.5),
           ylim=(-70, 5))
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    pilkku(ax)
    tallenna(fig, polku)


KUVAT = {
    "iir-askel": iir_askel, "iir-kuollut": iir_kuollut,
    "cordic-kierto": cordic_kierto, "nco-spektri": nco_spektri,
    "nco-sfdr": nco_sfdr, "cic-vaste": cic_vaste,
    "cic-integraattorit": cic_integraattorit,
    "mitattu-vaste": mitattu_vaste,
}


def main() -> None:
    kohde = Path(sys.argv[1])
    for nimi in sys.argv[2:] or list(KUVAT):
        KUVAT[nimi](kohde / f"{nimi}.png")
        print(f"{nimi}.png")


if __name__ == "__main__":
    main()
