"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Käyrät lasketaan
lukujen testattujen esimerkkien (esimerkit/) funktioilla ja samoilla
signaaleilla, joten kuvat näyttävät saman kuin tulostetaulukot.
"""

import contextlib
import importlib.util
import io
import math
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#B04848"          # alueen Laitteistosuunnittelu väri
KOROSTUS_VAALEA = "#F0DADA"
TOINEN = "#2F6F8F"
TOINEN_VAALEA = "#D5E6EE"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
HAALEA = "#EEF1F2"
MUSTE = "#1F2A2E"
MONO = "DejaVu Sans Mono"
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


def lataa(tiedosto: str) -> ModuleType:
    """Lataa esimerkkiohjelman moduulina; sen tulosteet ohitetaan."""
    nimi = "esimerkki_" + tiedosto.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(nimi, ESIMERKIT / tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    sys.modules[nimi] = moduuli
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(moduuli)
    return moduuli


def bittirivi(ax: Axes, y: float, tayte: list[str], tekstit: list[str],
              koko: float = 6.5) -> None:
    """Rivi bittilaatikoita; ylin bitti vasemmalla kohdassa x = 0."""
    for i, (vari, teksti) in enumerate(zip(tayte, tekstit, strict=True)):
        ax.add_patch(Rectangle((i, y), 1, 1, facecolor=vari,
                               edgecolor=HARMAA, linewidth=0.6))
        ax.text(i + 0.5, y + 0.5, teksti, ha="center", va="center",
                fontsize=koko, family=MONO)


# --- Luku 2: sama sana kolmessa muodossa ja lukusuora -----------------

def muodot(polku: Path) -> None:
    """Koodi 0x2800 tulkittuna Q1.15-, Q4.12- ja Q8.8-luvuksi sekä
    nelibittisen Q1.3-muodon kaikki arvot lukusuoralla."""
    koodi = 0x2800
    bitit = [(koodi >> (15 - i)) & 1 for i in range(16)]
    fig = uusi(6.4, 3.3)
    ax, suora = fig.subplots(2, 1, height_ratios=[3.2, 1.0])
    ax.set_axis_off()
    ax.set_xlim(-4.6, 19.4)
    ax.set_ylim(-0.4, 6.6)
    for rivi, (m, n) in enumerate(((1, 15), (4, 12), (8, 8))):
        y = 4.4 - 2.2 * rivi
        varit = [KOROSTUS_VAALEA if i < m else HAALEA for i in range(16)]
        varit[0] = KOROSTUS_VAALEA
        bittirivi(ax, y, varit, [str(b) for b in bitit])
        ax.plot([m, m], [y - 0.35, y + 1.35], color=KOROSTUS, linewidth=1.6)
        ax.text(m, y + 1.45, "pilkku", ha="center", va="bottom",
                fontsize=6.5, color=KOROSTUS)
        for i in (0, m - 1, m, 15):
            paino = m - 1 - i
            merkki = "−" if i == 0 else ""
            ax.text(i + 0.5, y - 0.12, f"{merkki}2$^{{{paino}}}$",
                    ha="center", va="top", fontsize=6, color=HARMAA)
        ax.text(-0.4, y + 0.5, f"Q{m}.{n}", ha="right", va="center",
                fontsize=9, fontweight="bold")
        ax.text(16.4, y + 0.5,
                f"= {koodi / 2**n:g}".replace(".", ","), ha="left",
                va="center", fontsize=9, family=MONO)
    ax.text(-0.4, 6.35, "koodi 0x2800", ha="right", va="center",
            fontsize=7.5, color=HARMAA)

    arvot = [k / 8 for k in range(-8, 8)]
    suora.plot([-1.08, 1.08], [0, 0], color=VAALEA, linewidth=1)
    suora.plot(arvot, [0] * len(arvot), "o", color=KOROSTUS, markersize=4)
    suora.plot([1.0], [0], "o", markerfacecolor="white",
               markeredgecolor=KOROSTUS, markersize=4)
    suora.annotate("+1 ei mahdu", (1.0, 0), (1.0, 0.75), ha="center",
                   fontsize=7, color=KOROSTUS,
                   arrowprops={"arrowstyle": "-", "color": KOROSTUS,
                               "linewidth": 0.6})
    suora.annotate("−1 mahtuu", (-1.0, 0), (-1.0, 0.75), ha="center",
                   fontsize=7, color=MUSTE,
                   arrowprops={"arrowstyle": "-", "color": HARMAA,
                               "linewidth": 0.6})
    suora.annotate("", (0.375, -0.5), (0.25, -0.5),
                   arrowprops={"arrowstyle": "<->", "color": HARMAA,
                               "linewidth": 0.7})
    suora.text(0.3125, -0.62, "LSB = 2$^{-3}$", ha="center", va="top",
               fontsize=7, color=HARMAA)
    suora.set_ylim(-1.4, 1.3)
    suora.set_xlim(-1.12, 1.12)
    suora.set_yticks([])
    suora.spines["left"].set_visible(False)
    suora.set_xticks([-1, -0.5, 0, 0.5, 1])
    suora.set_xlabel("Q1.3: neljän bitin kaikki 16 arvoa", fontsize=8)
    pilkku(suora)
    tallenna(fig, polku)


# --- Luku 3: tulon bittikentät ----------------------------------------

def tulo(polku: Path) -> None:
    """Q1.15 x Q1.15 = Q2.30 ja paluu Q1.15-muotoon."""
    fig = uusi(6.4, 1.75)
    ax = fig.add_subplot()
    ax.set_axis_off()
    ax.set_xlim(-0.6, 32.6)
    ax.set_ylim(-2.3, 2.9)
    varit = ([TOINEN_VAALEA] + [KOROSTUS_VAALEA] * 16 + [HAALEA] * 15)
    tekstit = ["s", "s"] + ["·"] * 30
    bittirivi(ax, 0, varit, tekstit, koko=6)
    ax.plot([2, 2], [-0.3, 1.3], color=KOROSTUS, linewidth=1.6)
    ax.text(2, 1.4, "pilkku", ha="center", va="bottom", fontsize=6.5,
            color=KOROSTUS)
    for x0, x1, teksti, vari in (
            (0, 1, "ylin bitti:\nsaturaatio,\njos ≠ etumerkki", TOINEN),
            (1, 17, "tulos Q1.15: bitit 30…15", KOROSTUS),
            (17, 32, "15 alinta bittiä pois: pyöristys", HARMAA)):
        ax.plot([x0 + 0.08, x1 - 0.08], [-0.45, -0.45], color=vari,
                linewidth=1.4)
        ax.text((x0 + x1) / 2 if x1 - x0 > 1 else 0.5, -0.65, teksti,
                ha="center" if x1 - x0 > 1 else "left", va="top",
                fontsize=7, color=vari)
    ax.text(0.5, 2.55, "bitti 31", ha="center", fontsize=6.5, color=HARMAA)
    ax.text(31.5, 2.55, "bitti 0", ha="center", fontsize=6.5, color=HARMAA)
    ax.text(16, 2.55, "32-bittinen tulo Q2.30", ha="center", fontsize=8)
    tallenna(fig, polku)


# --- Luku 4: pyöristystavat ja kuollut alue ---------------------------

def pyoristys(polku: Path) -> None:
    """Neljän pyöristystavan siirtofunktio nollan ympärillä."""
    h = lataa("04-harha.py")
    x = np.arange(-44, 45, dtype=np.int64)        # 1/16-askelin
    fig = uusi(6.4, 2.3)
    akselit = fig.subplots(1, 4, sharey=True)
    for ax, (nimi, tapa) in zip(akselit, (
            ("lattia", h.lattia), ("kohti nollaa", h.kohti_nollaa),
            ("puolikas ylöspäin", h.ylos),
            ("parilliseen", h.parilliseen)), strict=True):
        ax.plot([-2.8, 2.8], [-2.8, 2.8], color=VAALEA, linewidth=0.8)
        ax.step(x / h.YKSI, tapa(x), where="post", color=KOROSTUS,
                linewidth=1.3)
        puolikkaat = x[(x % h.YKSI) == h.YKSI // 2]
        ax.plot(puolikkaat / h.YKSI, tapa(puolikkaat), "o", color=MUSTE,
                markersize=2.6, zorder=3)
        ax.set_title(nimi, fontsize=8)
        ax.set_xticks([-2, -1, 0, 1, 2])
        ax.set_yticks([-3, -2, -1, 0, 1, 2, 3])
        ax.grid(alpha=0.3)
        ax.set_aspect("equal")
    akselit[0].set_ylabel("tulos")
    fig.supxlabel("arvo ennen pyöristystä (pisteet: tasapelit)", fontsize=8)
    tallenna(fig, polku)


def keskiarvo(polku: Path) -> None:
    """Liukuvan keskiarvon asettuminen kolmella toteutuksella."""
    h = lataa("04-harha.py")
    fig = uusi(6.4, 2.5)
    vasen, oikea = fig.subplots(1, 2, width_ratios=[1.2, 1])
    sarjat = (("lattia", h.lattia, 0, KOROSTUS, "-"),
              ("parilliseen", h.parilliseen, 0, MUSTE, "--"),
              ("lattia, tila +4 bittiä", h.lattia, 4, TOINEN, "-"))
    for ax, alue in ((vasen, (0, 120)), (oikea, (60, 160))):
        for nimi, tapa, murto, vari, tyyli in sarjat:
            for alku in (0, 2000):
                y = h.keskiarvo(tapa, alku, murto, 160)
                ax.plot(range(1, 161), y, tyyli, color=vari, linewidth=1.2,
                        label=nimi if alku == 0 else None)
        ax.axhline(1000, color=VAALEA, linewidth=0.8, zorder=0)
        ax.set_xlim(*alue)
        ax.set_xlabel("askel")
        ax.grid(alpha=0.3)
    vasen.set_ylabel("y")
    vasen.legend(frameon=False, fontsize=7, loc="upper right")
    oikea.set_ylim(980, 1012)
    oikea.set_title("suurennos tavoitteen ympäriltä", fontsize=8)
    oikea.text(158, 985.6, "985", ha="right", va="bottom", fontsize=7,
               color=KOROSTUS)
    oikea.text(158, 992.6, "992", ha="right", va="bottom", fontsize=7)
    oikea.text(158, 1008.4, "1008", ha="right", va="bottom", fontsize=7)
    tallenna(fig, polku)


# --- Luku 5: ylivuoto --------------------------------------------------

def ylivuoto(polku: Path) -> None:
    """Sama koe kuin esimerkissä 05-saturaatio.c: sini 0,6 kerrottuna
    kahdella, tulos kiertävällä ja saturoivalla summaimella."""
    v = lataa("05-valitulos.py")
    i = np.arange(64)
    x = [round(0.6 * 32767 * math.sin(k * 0.1)) for k in i]
    oikea = [2 * a / v.SKAALA for a in x]
    kierto = [v.kierra(2 * a) / v.SKAALA for a in x]
    saturaatio = [v.saturoi(2 * a) / v.SKAALA for a in x]
    fig = uusi(6.4, 2.4)
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, sarja, nimi in ((akselit[0], saturaatio, "saturaatio"),
                            (akselit[1], kierto, "kierto")):
        ax.axhspan(-1, 1 - 2**-15, color=HAALEA, zorder=0)
        ax.plot(i, oikea, color=VAALEA, linewidth=1.2, label="oikea arvo")
        ax.plot(i, sarja, color=KOROSTUS, linewidth=1.3, label=nimi)
        ax.set_xlabel("näyte")
        ax.set_yticks([-1, 0, 1])
        ax.legend(frameon=False, fontsize=7, loc="lower left")
    akselit[0].set_ylabel("arvo (harmaa alue: Q1.15)")
    tallenna(fig, polku)


def varahtely(polku: Path) -> None:
    """IIR-suodattimen vapaa vaste kiertävällä ja saturoivalla tilalla."""
    v = lataa("05-varahtely.py")
    fig = uusi(6.4, 2.3)
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, tapa, nimi in ((akselit[0], v.saturoi, "saturoiva tila"),
                           (akselit[1], v.kierra, "kiertävä tila")):
        y = v.vapaa_vaste(tapa, v.alku, -v.alku, 120)
        ax.plot(range(120), [a / v.SKAALA for a in y], color=KOROSTUS,
                linewidth=0.9, marker="o", markersize=1.6)
        ax.set_title(nimi, fontsize=8)
        ax.set_xlabel("näyte (syöte on nolla)")
        ax.set_yticks([-1, 0, 1])
        ax.grid(alpha=0.3)
    akselit[0].set_ylabel("y")
    tallenna(fig, polku)


# --- Luku 6: kvantisointikohina ---------------------------------------

def spektri_db(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ikkuna = np.hanning(len(x))
    s = np.abs(np.fft.rfft(x * ikkuna))
    return np.fft.rfftfreq(len(x)), 20 * np.log10(s / s.max() + 1e-12)


def spektri(polku: Path) -> None:
    """Neljä bittiä ilman ditheriä ja ditherillä sekä 16 bittiä."""
    s = lataa("06-sqnr.py")
    fig = uusi(6.4, 2.5)
    akselit = fig.subplots(1, 3, sharey=True)
    tapaukset = (("4 bittiä", s.kvantisoi(s.puoli, 4)),
                 ("4 bittiä ja dither", s.kvantisoi(s.puoli + s.tpdf, 4)),
                 ("16 bittiä", s.kvantisoi(s.puoli, 16)))
    for ax, (nimi, x) in zip(akselit, tapaukset, strict=True):
        f, db = spektri_db(x[:8192])
        ax.plot(f, db, color=KOROSTUS, linewidth=0.5)
        ax.set_title(nimi, fontsize=8)
        ax.set_xlabel("taajuus / $f_s$")
        ax.set_ylim(-150, 5)
        ax.set_xlim(0, 0.5)
        ax.grid(alpha=0.3)
        pilkku(ax)
    akselit[0].set_ylabel("taso (dB)")
    tallenna(fig, polku)


def sqnr(polku: Path) -> None:
    """Mitattu SQNR bittimäärän funktiona ja suora 6,02 b + 1,76."""
    s = lataa("06-sqnr.py")
    bitit = list(range(3, 17))
    mitattu = [s.sqnr_db(s.sini, s.kvantisoi(s.sini, b)) for b in bitit]
    fig = uusi(4.6, 2.5)
    ax = fig.add_subplot()
    ax.plot(bitit, [6.02 * b + 1.76 for b in bitit], color=VAALEA,
            linewidth=1.4, label="6,02 b + 1,76 dB")
    ax.plot(bitit, mitattu, "o", color=KOROSTUS, markersize=3.5,
            label="mitattu, täyden skaalan sini")
    ax.set(xlabel="bitit b", ylabel="SQNR (dB)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def kertoimet(polku: Path) -> None:
    """Taajuusvaste ideaalisilla ja kvantisoiduilla kertoimilla."""
    k = lataa("06-kertoimet.py")
    h = k.alipaasto(41, 0.1)
    f = np.fft.rfftfreq(1 << 14)
    fig = uusi(6.4, 2.7)
    ax = fig.add_subplot()
    for bitit, vari, leveys in ((6, VAALEA, 0.9), (8, TOINEN, 0.9),
                                (10, HARMAA, 0.9), (12, KOROSTUS, 1.0)):
        vaste = np.abs(np.fft.rfft(k.kvantisoi(h, bitit), 1 << 14))
        ax.plot(f, 20 * np.log10(vaste + 1e-9), color=vari,
                linewidth=leveys, label=f"{bitit} bittiä")
    vaste = np.abs(np.fft.rfft(h, 1 << 14))
    ax.plot(f, 20 * np.log10(vaste + 1e-9), color=MUSTE, linewidth=1.1,
            linestyle="--", label="double")
    ax.axvspan(0.15, 0.5, color=HAALEA, zorder=0)
    ax.text(0.325, -97, "estokaista", ha="center", fontsize=7.5,
            color=HARMAA)
    ax.set(xlabel="taajuus / $f_s$", ylabel="vaste (dB)", xlim=(0, 0.5),
           ylim=(-100, 10))
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=7.5, ncols=5, loc="upper right")
    pilkku(ax)
    tallenna(fig, polku)


# --- Luku 8: lohkoliukuluku --------------------------------------------

def lohkoliukuluku(polku: Path) -> None:
    """SQNR signaalin tason funktiona: Q1.15, lohkoliukuluku, binary32."""
    d = lataa("08-dynamiikka.py")
    tasot = np.arange(0, -81, -4)
    q, lohko, liuku = [], [], []
    for taso in tasot:
        x = 0.9 * 10 ** (taso / 20) * np.sin(2 * np.pi * 0.0123457 * d.n)
        q.append(d.sqnr(x, d.q15(x)))
        lohko.append(d.sqnr(x, d.lohkoliukuluku(x, 64)))
        liuku.append(d.sqnr(x, x.astype(np.float32).astype(np.float64)))
    fig = uusi(5.2, 2.6)
    ax = fig.add_subplot()
    ax.plot(tasot, liuku, "s-", color=HARMAA, markersize=2.5, linewidth=1,
            label="binary32 (24-bittinen mantissa)")
    ax.plot(tasot, lohko, "o-", color=TOINEN, markersize=2.5, linewidth=1.2,
            label="lohkoliukuluku, lohko 64, mantissa Q1.15")
    ax.plot(tasot, q, "o-", color=KOROSTUS, markersize=2.5, linewidth=1.2,
            label="Q1.15")
    ax.set(xlabel="signaalin taso (dB täydestä skaalasta)",
           ylabel="SQNR (dB)", ylim=(0, 165))
    ax.invert_xaxis()
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    tallenna(fig, polku)


KUVAT = {
    "muodot": muodot, "tulo": tulo, "pyoristys": pyoristys,
    "keskiarvo": keskiarvo, "ylivuoto": ylivuoto, "varahtely": varahtely,
    "spektri": spektri, "sqnr": sqnr, "kertoimet": kertoimet,
    "lohkoliukuluku": lohkoliukuluku,
}


def main() -> None:
    kohde = Path(sys.argv[1])
    valitut = sys.argv[2:] or list(KUVAT)
    for nimi in valitut:
        KUVAT[nimi](kohde / f"{nimi}.png")
        print(f"{nimi}.png")


if __name__ == "__main__":
    main()
