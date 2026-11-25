"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut tulevat
lukujen testatuista esimerkeistä (esimerkit/) tai samoista laskuista.
"""

import contextlib
import importlib.util
import io
import math
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, Rectangle, Wedge

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#6D4FA0"          # alueen Tietokonejärjestelmät väri
KOROSTUS_VAALEA = "#E4DCF0"
TOINEN = "#B07A2A"
TOINEN_VAALEA = "#F1E3CC"
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


def uusi(leveys: float = 4.6, korkeus: float = 2.8) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


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


def tyhja(ax: Axes) -> None:
    ax.set_axis_off()


# --- Luku 2: kahden komplementin lukuympyrä ---------------------------

def lukuympyra(polku: Path) -> None:
    """Neljän bitin kuviot ympyrällä: etumerkitön ja etumerkillinen
    tulkinta sekä kohdat, joissa kumpikin vuotaa yli."""
    fig = uusi(4.4, 4.1)
    ax = fig.add_subplot()
    ax.set_aspect("equal")
    tyhja(ax)
    ax.set(xlim=(-1.75, 1.75), ylim=(-1.62, 1.62))

    def kulma(k: float) -> float:        # myötäpäivään, nolla ylhäällä
        return math.pi / 2 - 2 * math.pi * k / 16

    # Negatiivisten kuvioiden puolisko (1000 ... 1111) sävytettynä.
    ax.add_patch(Wedge((0, 0), 1.42, math.degrees(kulma(15.5)),
                       math.degrees(kulma(7.5)), width=0.3,
                       facecolor=KOROSTUS_VAALEA, edgecolor="none"))
    for k in range(16):
        x, y = math.cos(kulma(k)), math.sin(kulma(k))
        etumerkillinen = k - 16 if k >= 8 else k
        ax.text(0.92 * x, 0.92 * y, f"{k:04b}", ha="center", va="center",
                family=MONO, fontsize=8)
        ax.text(0.62 * x, 0.62 * y, str(k), ha="center", va="center",
                color=HARMAA, fontsize=8)
        ax.text(1.27 * x, 1.27 * y, f"{etumerkillinen:+d}".replace("+0", "0"),
                ha="center", va="center", color=KOROSTUS, fontsize=9,
                fontweight="bold")
    # Ylivuotokohdat: sauma kuvioiden välissä.
    for sauma, vari, alku, loppu in ((15.5, HARMAA, 0.42, 0.78),
                                     (7.5, KOROSTUS, 1.08, 1.46)):
        x, y = math.cos(kulma(sauma)), math.sin(kulma(sauma))
        ax.plot([alku * x, loppu * x], [alku * y, loppu * y], color=vari,
                linewidth=1.6, linestyle=(0, (2, 1.4)))
    ax.text(0.0, 0.24, "etumerkitön:\n15 + 1 = 0", ha="center",
            va="center", color=HARMAA, fontsize=7)
    ax.text(0.2, -1.55, "etumerkillinen: 7 + 1 = −8", ha="left",
            va="center", color=KOROSTUS, fontsize=7.5)
    # +1 kulkee myötäpäivään.
    ax.add_patch(FancyArrowPatch(
        (0.42 * math.cos(kulma(2.6)), 0.42 * math.sin(kulma(2.6))),
        (0.42 * math.cos(kulma(5.4)), 0.42 * math.sin(kulma(5.4))),
        connectionstyle="arc3,rad=-0.3", arrowstyle="-|>",
        mutation_scale=9, color=MUSTE, linewidth=1))
    ax.text(0.0, -0.06, "+1", ha="center", va="center", fontsize=10)
    ax.text(0.0, -0.22, "myötäpäivään", ha="center", va="center",
            fontsize=6.5, color=HARMAA)
    ax.text(-1.72, 1.52, "sisäkehä: etumerkitön arvo", color=HARMAA,
            fontsize=7.5, va="center")
    ax.text(-1.72, 1.38, "ulkokehä: kahden komplementti", color=KOROSTUS,
            fontsize=7.5, va="center")
    tallenna(fig, polku)


# --- Luku 4: bittikentät ------------------------------------------------

Kentta = tuple[str, int, str]            # nimi, leveys, selite


def kentta(sana: int, alku: int, leveys: int) -> int:
    """Sama kuin esimerkin 04-otsake.c funktio kentta."""
    return (sana >> alku) & ((1 << leveys) - 1)


def piirra_kentat(ax: Axes, sana: int, bitteja: int,
                  kentat: list[Kentta], otsikko: str,
                  bittikoko: float = 7.0) -> None:
    """Sana kenttinä: eniten merkitsevä bitti vasemmalla."""
    tyhja(ax)
    ax.set(xlim=(-0.3, bitteja + 0.3), ylim=(-1.25, 1.75))
    ax.text(0, 1.5, otsikko, fontsize=8.5, fontweight="bold", va="center")
    paikka = 0
    for i, (nimi, leveys, selite) in enumerate(kentat):
        alku = bitteja - paikka - leveys         # kentän alin bitti
        vari = KOROSTUS_VAALEA if i % 2 == 0 else TOINEN_VAALEA
        ax.add_patch(Rectangle((paikka, 0), leveys, 0.7, facecolor=vari,
                               edgecolor=MUSTE, linewidth=0.8))
        bitit = f"{kentta(sana, alku, leveys):0{leveys}b}"
        for j, b in enumerate(bitit):
            ax.text(paikka + j + 0.5, 0.35, b, ha="center", va="center",
                    family=MONO, fontsize=bittikoko)
        ax.text(paikka + leveys / 2, 0.98, nimi, ha="center", va="center",
                fontsize=7.5)
        ax.text(paikka + leveys / 2, -0.32, selite, ha="center",
                va="center", fontsize=7, color=HARMAA)
        ax.text(paikka + 0.5, -0.86, str(alku + leveys - 1), ha="center",
                va="center", fontsize=6, color=HARMAA)
        if leveys > 1:
            ax.text(paikka + leveys - 0.5, -0.86, str(alku), ha="center",
                    va="center", fontsize=6, color=HARMAA)
        paikka += leveys


def bittikentat(polku: Path) -> None:
    """IPv4-otsakkeen ensimmäinen sana ja RGB565-pikseli kenttinä."""
    fig = uusi(6.3, 2.5)
    ylempi, alempi = fig.subplots(2, 1)
    sana = int.from_bytes(bytes([0x45, 0xb8, 0x05, 0xdc]), "big")
    piirra_kentat(ylempi, sana, 32, [
        ("versio", 4, "4"), ("pituus", 4, "5 · 4 = 20"),
        ("DSCP", 6, "46"), ("ECN", 2, "0"),
        ("kokonaispituus", 16, "1500 tavua")],
        "IPv4-otsakkeen ensimmäinen sana 0x45b805dc")
    piirra_kentat(alempi, 0xfc00, 16, [
        ("punainen", 5, "31 → 255"), ("vihreä", 6, "32 → 130"),
        ("sininen", 5, "0 → 0")],
        "RGB565-pikseli 0xfc00", bittikoko=8.0)
    alempi.set(xlim=(-0.3, 32.3))        # sama bitin leveys kuin yllä
    tallenna(fig, polku)


# --- Luku 5: katkaiseva ja lattiajako ---------------------------------

def jako(polku: Path) -> None:
    """Osamäärä ja jäännös jakajalla 3: C katkaisee, Python pyöristää
    alas."""
    fig = uusi(6.0, 2.6)
    vasen, oikea = fig.subplots(1, 2)
    a = list(range(-9, 10))
    c_osa = [math.trunc(x / 3) for x in a]
    c_jaannos = [int(math.fmod(x, 3)) for x in a]
    py_osa = [x // 3 for x in a]
    py_jaannos = [x % 3 for x in a]
    for ax, c, py, nimi in ((vasen, c_osa, py_osa, "osamäärä a / 3"),
                            (oikea, c_jaannos, py_jaannos,
                             "jäännös a % 3")):
        ax.axhline(0, color=VAALEA, linewidth=0.6)
        ax.axvline(0, color=VAALEA, linewidth=0.6)
        ax.plot(a, c, "o", color=HARMAA, markersize=5.5, markerfacecolor="white",
                label="C: kohti nollaa")
        ax.plot(a, py, "o", color=KOROSTUS, markersize=2.6,
                label="Python: alaspäin")
        ax.set(xlabel="a", title=nimi, xticks=range(-9, 10, 3))
        ax.title.set_fontsize(9)
        ax.tick_params(labelsize=8)
    vasen.set_yticks(range(-3, 4))
    oikea.set_yticks(range(-2, 3))
    vasen.legend(frameon=False, fontsize=7.5, loc="upper left")
    tallenna(fig, polku)


# --- Luku 6: liukuluvun kentät, lukusuora ja ulp ------------------------

def liukukentat(polku: Path) -> None:
    """Luku -2,5 binary16-muodossa bitti bitiltä."""
    fig = uusi(5.2, 1.75)
    ax = fig.add_subplot()
    tyhja(ax)
    ax.set(xlim=(-0.3, 16.3), ylim=(-1.9, 1.6))
    (koodi,) = struct.unpack(">H", struct.pack(">e", -2.5))
    osat = [("etumerkki", 1, HAALEA), ("eksponentti", 5, TOINEN_VAALEA),
            ("mantissa", 10, KOROSTUS_VAALEA)]
    paikka = 0
    for nimi, leveys, vari in osat:
        ax.add_patch(Rectangle((paikka, 0), leveys, 0.75, facecolor=vari,
                               edgecolor=MUSTE, linewidth=0.8))
        alku = 16 - paikka - leveys
        for j, b in enumerate(f"{kentta(koodi, alku, leveys):0{leveys}b}"):
            ax.text(paikka + j + 0.5, 0.375, b, ha="center", va="center",
                    family=MONO, fontsize=9)
        ax.text(paikka + leveys / 2, 1.1, nimi, ha="center", va="center",
                fontsize=8)
        paikka += leveys
    ax.text(0.5, -0.4, "1: negatiivinen", ha="center", va="center",
            fontsize=7, color=HARMAA)
    ax.text(3.5, -0.4, "16 − bias 15 = +1", ha="center", va="center",
            fontsize=7, color=HARMAA)
    ax.text(11, -0.4, "piilobitti 1 ja bitit 01…: 1,01₂ = 1,25",
            ha="center", va="center", fontsize=7, color=HARMAA)
    ax.text(8, -1.35, "−1 · 1,25 · 2¹ = −2,5", ha="center", va="center",
            fontsize=10)
    tallenna(fig, polku)


def lukusuora(polku: Path) -> None:
    """Kuuden bitin lelumuodon kaikki positiiviset arvot lukusuoralla."""
    pienet = lataa("08-pienet.py")
    lelu = pienet.Muoto("lelu", 3, 2)
    koodit = range(1, 1 << 5)                    # positiiviset, ei nollaa
    arvot = [(lelu.arvo(k), k >> 2) for k in koodit]
    arvot = [(a, e) for a, e in arvot if math.isfinite(a)]
    fig = uusi(6.2, 3.5)
    koko, alku, logi = fig.subplots(3, 1, height_ratios=[1, 1.35, 1])

    def viivat(ax: Axes, y0: float, y1: float, mukana: bool = True) -> None:
        for a, e in arvot:
            if e == 0 and not mukana:
                continue
            vari = TOINEN if e == 0 else (KOROSTUS if e % 2 else HARMAA)
            ax.plot([a, a], [y0, y1], color=vari, linewidth=1.3)

    for ax in (koko, alku, logi):
        ax.spines["left"].set_visible(False)
        ax.set_yticks([])
        ax.tick_params(labelsize=7.5)
    viivat(koko, 0, 1)
    koko.plot([0, 0], [0, 1], color=MUSTE, linewidth=1.3)
    koko.set(xlim=(-0.2, 14.4), ylim=(0, 1.9),
             xticks=[0, 1, 2, 4, 8, 14])
    for a, teksti in ((1.5, "väli 0,25"), (3, "0,5"), (6, "1"), (11, "2")):
        koko.text(a, 1.35, teksti, ha="center", fontsize=7, color=HARMAA)
    koko.set_title("Kaikki arvot: väli kaksinkertaistuu, kun eksponentti "
                   "kasvaa", fontsize=8, loc="left")

    viivat(alku, 1.6, 2.6)
    viivat(alku, 0, 1, mukana=False)
    for y in (0, 1.6):
        alku.plot([0, 0], [y, y + 1], color=MUSTE, linewidth=1.3)
    alku.set(xlim=(-0.02, 1.03), ylim=(0, 3.5),
             xticks=[0, 0.0625, 0.25, 0.5, 1],
             xticklabels=["0", "0,0625", "0,25", "0,5", "1"])
    alku.text(0.125, 2.85, "subnormaalit", ha="center", fontsize=7,
              color=TOINEN)
    alku.text(0.27, 2.85, "pienin normaali 0,25", ha="left", fontsize=7,
              color=HARMAA)
    alku.annotate("", xy=(0.004, 0.3), xytext=(0.246, 0.3),
                  arrowprops={"arrowstyle": "<->", "color": TOINEN,
                              "linewidth": 0.9})
    alku.text(0.125, 0.55, "aukko ilman subnormaaleja", ha="center",
              fontsize=6.2, color=TOINEN)
    alku.set_title("Suurennos nollan läheltä: ylhäällä subnormaalien "
                   "kanssa, alhaalla ilman", fontsize=8, loc="left")

    for a, e in arvot:
        if e > 0:
            vari = KOROSTUS if e % 2 else HARMAA
            logi.plot([a, a], [0, 1], color=vari, linewidth=1.3)
    logi.set_xscale("log", base=2)
    logi.set(xlim=(0.22, 16), ylim=(0, 1.3),
             xticks=[0.25, 0.5, 1, 2, 4, 8],
             xticklabels=["0,25", "0,5", "1", "2", "4", "8"])
    logi.set_title("Logaritmisella asteikolla: jokaisessa kahden potenssin "
                   "välissä on yhtä monta arvoa", fontsize=8, loc="left")
    tallenna(fig, polku)


def ulp(polku: Path) -> None:
    """Peräkkäisten lukujen väli luvun suuruuden funktiona."""
    fig = uusi(5.4, 3.2)
    ax = fig.add_subplot()
    x = np.logspace(0, 17, 1400)
    sarjat: list[tuple[Any, str, str, float]] = [
        (np.float16, "binary16", VAALEA, 6.5e4),
        (np.float32, "binary32 (float)", KOROSTUS, 1e17),
        (np.float64, "binary64 (double)", HARMAA, 1e17)]
    for tyyppi, nimi, vari, raja in sarjat:
        xs = x[x < raja]
        ax.loglog(xs, np.spacing(xs.astype(tyyppi)).astype(np.float64),
                  color=vari, linewidth=1.3, label=nimi)
    ax.axhline(1, color=MUSTE, linewidth=0.6, linestyle=(0, (4, 3)))
    ax.text(8e8, 1.8, "väli 1: osa kokonaisluvuista jää väliin",
            fontsize=7, color=MUSTE)
    for raja, teksti in ((2.0 ** 24, "$2^{24}$"), (2.0 ** 53, "$2^{53}$")):
        ax.plot([raja], [1], "o", color=MUSTE, markersize=3)
        ax.text(raja * 2.5, 0.08, teksti, ha="left", fontsize=7.5)
    # Luvun 6 kello: 1 ms:n lisäys katoaa, kun se on alle puoli väliä.
    ax.axhline(0.002, color=TOINEN, linewidth=0.6, linestyle=(0, (4, 3)))
    ax.plot([32768], [float(np.spacing(np.float32(32768)))], "o",
            color=TOINEN, markersize=3.5)
    ax.annotate("float-kello pysähtyy:\n32 768 s, väli 0,0039 s",
                xy=(32768, 0.0039), xytext=(3e6, 2e-5), fontsize=7,
                color=TOINEN,
                arrowprops={"arrowstyle": "-", "color": TOINEN,
                            "linewidth": 0.7})
    ax.text(7e16, 0.0032, "väli 2 ms", fontsize=7, color=TOINEN,
            ha="right")
    ax.set(xlabel="luvun suuruus", ylabel="väli seuraavaan lukuun (ulp)",
           xlim=(1, 1e17), ylim=(1e-16, 1e3))
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    tallenna(fig, polku)


# --- Luku 7: pyöristystilat ja summauksen virhe -------------------------

def pyoristystilat(polku: Path) -> None:
    """Neljä pyöristystilaa lukusuoralla: nuoli arvosta tulokseen."""
    fig = uusi(5.6, 2.5)
    ax = fig.add_subplot()
    tilat: list[tuple[str, Any]] = [
        ("lähimpään,\ntasapelit parilliseen", round),
        ("kohti nollaa", math.trunc),
        ("ylös", math.ceil),
        ("alas", math.floor)]
    arvot = [-2.5, -1.7, -0.5, 0.5, 1.3, 2.5]
    for rivi, (nimi, funktio) in enumerate(tilat):
        y = len(tilat) - 1 - rivi
        ax.plot([-3.2, 3.2], [y, y], color=VAALEA, linewidth=0.7)
        for k in range(-3, 4):
            ax.plot([k, k], [y - 0.09, y + 0.09], color=HARMAA,
                    linewidth=0.8)
        ax.text(-3.45, y, nimi, ha="right", va="center", fontsize=7.5)
        for x in arvot:
            tulos = funktio(x)
            ax.plot([x], [y], "o", color=MUSTE, markersize=2.8)
            ax.add_patch(FancyArrowPatch(
                (x, y + 0.04), (tulos, y + 0.04),
                connectionstyle="arc3,rad=-0.55" if tulos > x
                else "arc3,rad=0.55",
                arrowstyle="-|>", mutation_scale=7, color=KOROSTUS,
                linewidth=1))
    ax.set(xlim=(-5.6, 3.4), ylim=(-0.5, len(tilat) - 0.35), yticks=[],
           xticks=range(-3, 4))
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_bounds(-3, 3)
    ax.tick_params(labelsize=8)
    tallenna(fig, polku)


def summaus(polku: Path) -> None:
    """Suhteellinen virhe lukemien määrän funktiona: esimerkin
    07-summaus.c ohjelma käännetään ja ajetaan argumentilla kayra."""
    kaantaja = shutil.which("gcc-14") or shutil.which("cc")
    assert kaantaja is not None
    with tempfile.TemporaryDirectory() as hak:
        ohjelma = str(Path(hak) / "summaus")
        subprocess.run([kaantaja, "-std=c23", "-O1",
                        str(ESIMERKIT / "07-summaus.c"), "-o", ohjelma,
                        "-lm"], check=True)
        tuloste = subprocess.run([ohjelma, "kayra"], check=True,
                                 capture_output=True, text=True).stdout
    data = np.array([[float(s) for s in rivi.split()]
                     for rivi in tuloste.splitlines()])
    fig = uusi(4.8, 2.9)
    ax = fig.add_subplot()
    for sarake, nimi, vari, tyyli in ((1, "naiivi silmukka", KOROSTUS, "-"),
                                      (3, "parittainen", HARMAA, "-"),
                                      (2, "Kahan", MUSTE, "--")):
        ax.loglog(data[:, 0], np.maximum(data[:, sarake], 1e-9), tyyli,
                  color=vari, linewidth=1.3, label=nimi)
    ax.axhline(2.0 ** -24, color=VAALEA, linewidth=0.7)
    ax.text(1.2e7, 8.5e-8, "floatin tarkkuus $2^{-24}$", fontsize=7,
            color=HARMAA, ha="right")
    ax.set(xlabel="lukemien määrä", ylabel="suhteellinen virhe",
           ylim=(1e-9, 1))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    tallenna(fig, polku)


# --- Luku 8: muotojen bittijako ja kvantisointi -------------------------

def muodot(polku: Path) -> None:
    """Liukulukumuotojen kentät samassa mittakaavassa."""
    fig = uusi(6.2, 2.5)
    ax = fig.add_subplot()
    tyhja(ax)
    rivit = [("binary32 (float)", 8, 23), ("bfloat16", 8, 7),
             ("binary16", 5, 10), ("FP8 E5M2", 5, 2), ("FP8 E4M3", 4, 3)]
    ax.set(xlim=(-9.5, 32.4), ylim=(-0.3, len(rivit) + 0.55))
    for i, (nimi, e, m) in enumerate(rivit):
        y = len(rivit) - 1 - i
        ax.text(-0.5, y + 0.3, nimi, ha="right", va="center", fontsize=8)
        paikka = 0
        for leveys, vari, teksti in ((1, HAALEA, "±"),
                                     (e, TOINEN_VAALEA, f"eksponentti {e}"),
                                     (m, KOROSTUS_VAALEA, f"mantissa {m}")):
            ax.add_patch(Rectangle((paikka, y), leveys, 0.6, facecolor=vari,
                                   edgecolor=MUSTE, linewidth=0.8))
            if leveys < 4:
                teksti = teksti.split()[-1]
            elif leveys < 8:
                teksti = teksti[0] + " " + teksti.split()[-1]
            ax.text(paikka + leveys / 2, y + 0.3, teksti, ha="center",
                    va="center", fontsize=7)
            paikka += leveys
    # bfloat16 on binary32:n ylin puolisko.
    ax.plot([16, 16], [3 - 0.12, 4 + 0.72], color=KOROSTUS, linewidth=1,
            linestyle=(0, (3, 2)))
    ax.text(16.3, 3.3, "sama kuin floatin 16 ylintä bittiä", fontsize=7,
            color=KOROSTUS, va="center")
    for b in (0, 8, 16, 24, 32):
        ax.text(b, len(rivit) + 0.2, str(b), ha="center", fontsize=6.5,
                color=HARMAA)
    ax.text(-0.5, len(rivit) + 0.2, "bittejä", ha="right", fontsize=6.5,
            color=HARMAA)
    tallenna(fig, polku)


def kvantisointi(polku: Path) -> None:
    """Symmetrinen int8-kvantisointi: porras ja virhe (esimerkin
    08-kvantisointi.py funktio kvantisoi_painot)."""
    esimerkki = lataa("08-kvantisointi.py")
    w = np.linspace(-0.5, 0.5, 20001, dtype=np.float32)
    q, skaala = esimerkki.kvantisoi_painot(w)
    takaisin = q.astype(np.float64) * skaala
    fig = uusi(6.0, 2.6)
    vasen, oikea = fig.subplots(1, 2)
    alue = np.abs(w) < 0.02
    vasen.plot(w[alue], w[alue], color=VAALEA, linewidth=1,
               label="alkuperäinen")
    vasen.plot(w[alue], takaisin[alue], color=KOROSTUS, linewidth=1.3,
               label="int8 ja takaisin")
    vasen.set(xlabel="paino", ylabel="esitetty arvo",
              title="255 tasoa: porras 0,0039")
    vasen.legend(frameon=False, fontsize=7.5, loc="upper left")
    oikea.plot(w[alue], (takaisin - w)[alue], color=KOROSTUS, linewidth=1)
    for raja in (-skaala / 2, skaala / 2):
        oikea.axhline(raja, color=HARMAA, linewidth=0.6,
                      linestyle=(0, (4, 3)))
    oikea.text(-0.019, skaala / 2 * 1.12, "± puoli porrasta", fontsize=7,
               color=HARMAA)
    oikea.set(xlabel="paino", ylabel="virhe", title="pyöristysvirhe",
              ylim=(-skaala * 0.75, skaala * 0.75))
    for ax in (vasen, oikea):
        ax.title.set_fontsize(9)
        ax.tick_params(labelsize=7.5)
    tallenna(fig, polku)


# --- Luku 9: stokastinen pyöristys ---------------------------------------

def stokastinen(polku: Path) -> None:
    """Määritelmä lukusuoralla: todennäköisyydet etäisyyksien mukaan."""
    fig = uusi(5.0, 1.55)
    ax = fig.add_subplot()
    tyhja(ax)
    ax.set(xlim=(-0.45, 1.45), ylim=(-0.75, 1.0))
    ax.plot([-0.35, 1.35], [0, 0], color=HARMAA, linewidth=0.8)
    for k, teksti in ((0, "alempi naapuri"), (1, "ylempi naapuri")):
        ax.plot([k, k], [-0.1, 0.1], color=MUSTE, linewidth=1.2)
        ax.text(k, -0.4, teksti, ha="center", fontsize=7.5)
    x = 0.3
    ax.plot([x], [0], "o", color=MUSTE, markersize=4)
    ax.text(x, -0.4, "x", ha="center", fontsize=8.5, style="italic")
    for kohde, kaari, teksti, paikka in ((0, 0.6, "alas: 70 %", 0.05),
                                         (1, -0.3, "ylös: 30 %", 0.95)):
        ax.add_patch(FancyArrowPatch(
            (x, 0.07), (kohde, 0.07), connectionstyle=f"arc3,rad={kaari}",
            arrowstyle="-|>", mutation_scale=9, color=KOROSTUS,
            linewidth=1.2))
        ax.text(paikka, 0.5, teksti, ha="center", fontsize=8,
                color=KOROSTUS)
    ax.annotate("", xy=(0, -0.62), xytext=(x, -0.62),
                arrowprops={"arrowstyle": "<->", "color": HARMAA,
                            "linewidth": 0.7})
    ax.text(x / 2, -0.74, "0,3 väliä", ha="center", va="top", fontsize=6.5,
            color=HARMAA)
    tallenna(fig, polku)


def paivitys(polku: Path) -> None:
    """Painon oppiminen neljällä pyöristystavalla (esimerkin
    09-paivitys.py polut)."""
    esimerkki = lataa("09-paivitys.py")
    fig = uusi(5.0, 2.9)
    ax = fig.add_subplot()
    ax.axhline(esimerkki.TAVOITE, color=VAALEA, linewidth=0.7)
    tyylit = {"tarkka": (MUSTE, "--", 1.0),
              "katkaisu": (TOINEN, "-", 1.3),
              "lähimpään": (HARMAA, "-", 1.3),
              "stokastinen": (KOROSTUS, "-", 1.0)}
    for nimi, polku_w in esimerkki.POLUT.items():
        vari, tyyli, paksuus = tyylit[nimi]
        ax.plot(polku_w, tyyli, color=vari, linewidth=paksuus, label=nimi)
    ax.text(596, esimerkki.TAVOITE + 0.012, "tavoite 0,7", ha="right",
            fontsize=7, color=HARMAA)
    ax.set(xlabel="askel", ylabel="paino", xlim=(0, 600), ylim=(0, 0.78))
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    tallenna(fig, polku)


# --- Luku 10: matriisi muistissa -----------------------------------------

def jarjestys(polku: Path) -> None:
    """3 x 4 -matriisi ja sen alkiot muistissa rivi- ja
    sarakejärjestyksessä."""
    fig = uusi(6.2, 2.3)
    ax = fig.add_subplot()
    tyhja(ax)
    ax.set_aspect("equal")
    ax.set(xlim=(-0.2, 19.4), ylim=(-0.5, 4.6))
    varit = [KOROSTUS_VAALEA, TOINEN_VAALEA, HAALEA]

    def ruutu(x: float, y: float, i: int, j: int) -> None:
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor=varit[i],
                               edgecolor=MUSTE, linewidth=0.7))
        ax.text(x + 0.5, y + 0.5, f"{i},{j}", ha="center", va="center",
                fontsize=7, family=MONO)

    for i in range(3):
        for j in range(4):
            ruutu(j, 3 - i, i, j)
    ax.text(2, 0.55, "matriisi (rivi, sarake)", ha="center", fontsize=7.5)
    riveittain = [(i, j) for i in range(3) for j in range(4)]
    sarakkeittain = [(i, j) for j in range(4) for i in range(3)]
    for y, alkiot, nimi in ((2.9, riveittain, "rivijärjestys: C, NumPy"),
                            (0.3, sarakkeittain,
                             "sarakejärjestys: Fortran, MATLAB, Julia")):
        for k, (i, j) in enumerate(alkiot):
            ruutu(6.6 + k, y, i, j)
            ax.text(7.1 + k, y - 0.32, str(k * 8), ha="center",
                    fontsize=5.5, color=HARMAA)
        ax.text(6.6, y + 1.25, nimi, fontsize=7.5)
    ax.text(18.9, 2.58, "tavu", fontsize=5.5, color=HARMAA, ha="left")
    tallenna(fig, polku)


KUVAT = {
    "lukuympyra": lukuympyra, "bittikentat": bittikentat, "jako": jako,
    "liukukentat": liukukentat, "lukusuora": lukusuora, "ulp": ulp,
    "pyoristystilat": pyoristystilat, "summaus": summaus,
    "muodot": muodot, "kvantisointi": kvantisointi,
    "stokastinen": stokastinen, "paivitys": paivitys,
    "jarjestys": jarjestys,
}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    valitut = sys.argv[2:] or list(KUVAT)
    for kuva in valitut:
        KUVAT[kuva](kohde / f"{kuva}.png")
