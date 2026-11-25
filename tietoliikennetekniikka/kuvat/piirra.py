"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE [KUVA ...]

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Käyrät ja pisteet
lasketaan lukujen testatuilla esimerkeillä (esimerkit/), jotka ladataan
moduuleina.
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
from matplotlib.patches import Circle, Polygon, Rectangle

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#3D5A73"          # alueen Verkot ja hajautetut järjestelmät sävy
KOROSTUS_VAALEA = "#D5DEE6"
TOINEN = "#B07A2A"
TOINEN_VAALEA = "#F1E3CC"
KOLMAS = "#3E7F3C"
KOLMAS_VAALEA = "#D9E8D8"
PUNAINEN = "#B04848"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
HAALEA = "#EEF1F2"
MUSTE = "#1F2A2E"
MONO = "DejaVu Sans Mono"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 8
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA
rcParams["legend.frameon"] = False
rcParams["grid.color"] = HAALEA
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 5.6, korkeus: float = 2.6) -> Figure:
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


# --- Luku 2: vaimennus --------------------------------------------------

def kupari(polku: Path) -> None:
    m = lataa("02-kupari.py")
    fig = uusi(4.6, 2.5)
    ax = fig.add_subplot()
    f = np.linspace(1, 250, 300)
    ax.plot(f, [m.vaimennus_db(x) for x in f], color=KOROSTUS, label="100 m")
    ax.plot(f, [m.vaimennus_db(x, 50) for x in f], color=TOINEN,
            label="50 m")
    a = m.vaimennus_db(100)
    ax.plot([100], [a], "o", color=KOROSTUS, markersize=4)
    ax.annotate(f"100 MHz: {a:.1f} dB\n(1 % tehosta jäljellä)"
                .replace(".", ","), (100, a), (128, 1.5), fontsize=7,
                arrowprops={"arrowstyle": "-", "color": HARMAA,
                            "linewidth": 0.6})
    ax.set(xlabel="taajuus (MHz)", ylabel="vaimennus (dB)",
           xlim=(0, 250), ylim=(0, 35))
    ax.legend(loc="upper left")
    ax.grid(True)
    tallenna(fig, polku)


def radio(polku: Path) -> None:
    m = lataa("02-radio.py")
    fig = uusi(4.6, 2.5)
    ax = fig.add_subplot()
    d = np.logspace(0, 3, 100)
    ax.semilogx(d, [m.fspl_db(x, 5.5e9) for x in d], color=TOINEN,
                label="5,5 GHz")
    ax.semilogx(d, [m.fspl_db(x, 2.4e9) for x in d], color=KOROSTUS,
                label="2,4 GHz")
    taso = m.fspl_db(100, 2.4e9)
    ax.annotate("", (100, taso), (10, taso),
                arrowprops={"arrowstyle": "<-", "color": HARMAA,
                            "linewidth": 0.7})
    ax.annotate("", (10, m.fspl_db(10, 2.4e9)), (10, taso),
                arrowprops={"arrowstyle": "<-", "color": HARMAA,
                            "linewidth": 0.7})
    ax.text(30, 82, "etäisyys ×10", ha="center", fontsize=7, color=HARMAA)
    ax.text(8.5, 70, "+20 dB", ha="right", va="center", fontsize=7,
            color=HARMAA)
    ax.set(xlabel="etäisyys (m)", ylabel="vaimennus (dB)", ylim=(35, 112))
    ax.set_xticks([1, 10, 100, 1000], ["1", "10", "100", "1000"])
    ax.legend(loc="lower right")
    ax.grid(True)
    tallenna(fig, polku)


# --- Luku 3: Shannon ----------------------------------------------------

def shannon(polku: Path) -> None:
    m = lataa("03-shannon.py")
    fig = uusi(4.6, 2.7)
    ax = fig.add_subplot()
    snr = np.linspace(0, 40, 200)
    for kaista, vari in ((40e6, TOINEN), (20e6, KOROSTUS)):
        ax.plot(snr, [m.shannon(kaista, s) / 1e6 for s in snr], color=vari,
                label=f"B = {kaista / 1e6:.0f} MHz")
    for s in (5.0, 25.0):
        c = m.shannon(20e6, s) / 1e6
        ax.plot([s], [c], "o", color=KOROSTUS, markersize=4)
        ax.annotate(f"{c:.0f} Mbit/s", (s, c), (s + 1, c - 38), fontsize=7)
    c20, c40 = m.shannon(20e6, 34.0) / 1e6, m.shannon(40e6, 34.0) / 1e6
    ax.annotate("", (34, c40), (34, c20),
                arrowprops={"arrowstyle": "->", "color": HARMAA,
                            "linewidth": 0.7})
    ax.text(33.3, (c20 + c40) / 2, "kaista ×2:\nkapasiteetti ×2",
            ha="right", va="center", fontsize=7, color=HARMAA)
    ax.set(xlabel="signaali-kohinasuhde (dB)", ylabel="kapasiteetti (Mbit/s)",
           xlim=(0, 40), ylim=(0, 560))
    ax.legend(loc="upper left")
    ax.grid(True)
    tallenna(fig, polku)


# --- Luku 4: linjakoodit, PAM4 ja konstellaatiot -------------------------

def porras(ax: Axes, tasot: list[int], kesto: float, vari: str) -> None:
    x = [i * kesto for i in range(len(tasot) + 1)]
    ax.step(x, [*tasot, tasot[-1]], where="post", color=vari, linewidth=1.4)


def linjakoodit(polku: Path) -> None:
    m = lataa("04-linjakoodit.py")
    bitit = "00001101"
    fig = uusi(5.6, 3.3)
    akselit = fig.subplots(4, 1, sharex=True)
    koodattu = m.koodaa_4b5b(bitit)
    rivit = [
        ("NRZ", m.nrz(bitit), 1.0, None),
        ("NRZI", m.nrzi(bitit), 1.0, None),
        ("Manchester", m.manchester(bitit), 0.5, None),
        ("4B5B + NRZI", m.nrzi(koodattu), 0.8, koodattu),
    ]
    for ax, (nimi, tasot, kesto, koodi) in zip(akselit, rivit, strict=True):
        for k in range(len(bitit) + 1):
            ax.axvline(k, color=HAALEA, linewidth=0.8, zorder=0)
        porras(ax, tasot, kesto, KOROSTUS)
        ax.set(ylim=(-1.5, 1.9), yticks=[], xlim=(0, len(bitit)))
        ax.set_ylabel(nimi, rotation=0, ha="right", va="center", fontsize=8)
        for sivu in ("left", "bottom"):
            ax.spines[sivu].set_visible(False)
        ax.tick_params(bottom=False, labelbottom=False)
        if koodi:
            for k, b in enumerate(koodi):
                ax.text((k + 0.5) * kesto, 1.35, b, ha="center",
                        family=MONO, fontsize=6.5, color=TOINEN)
    for k, b in enumerate(bitit):
        akselit[0].text(k + 0.5, 1.4, b, ha="center", family=MONO,
                        fontsize=8.5)
    tallenna(fig, polku)


def pam4(polku: Path) -> None:
    m = lataa("04-pam4.py")
    fig = uusi(4.6, 1.9)
    ax = fig.add_subplot()
    symbolit = m.symbolit
    for taso in (-3, -1, 1, 3):
        ax.axhline(taso, color=HAALEA, linewidth=0.8, zorder=0)
    porras(ax, symbolit, 1.0, KOROSTUS)
    for k, s in enumerate(symbolit):
        ax.text(k + 0.5, 3.9, m.BITIT[s], ha="center", family=MONO,
                fontsize=8)
    ax.set(yticks=[-3, -1, 1, 3], ylim=(-3.8, 4.8),
           xlim=(0, len(symbolit)), xlabel="symboli")
    ax.set_yticklabels([f"{m.BITIT[t]}  {t:+d}" for t in (-3, -1, 1, 3)],
                       family=MONO)
    ax.set_xticks(range(len(symbolit) + 1))
    tallenna(fig, polku)


def konstellaatio(polku: Path) -> None:
    m = lataa("04-konstellaatio.py")
    rng = np.random.default_rng(40)
    fig = uusi(5.8, 2.25)
    akselit = fig.subplots(1, 3)
    snr_db = 16.0
    hajonta = math.sqrt(10 ** (-snr_db / 10) / 2)
    for ax, (nimi, bitteja) in zip(
            akselit, (("QPSK", 2), ("16-QAM", 4), ("64-QAM", 6)),
            strict=True):
        pisteet = m.qam(bitteja)
        arvot = np.array(list(pisteet.values()))
        lahetetty = arvot[rng.integers(len(arvot), size=1500)]
        kohina = hajonta * (rng.standard_normal(1500)
                            + 1j * rng.standard_normal(1500))
        v = lahetetty + kohina
        ax.plot(v.real, v.imag, ".", color=VAALEA, markersize=1.5,
                zorder=1)
        ax.plot(arvot.real, arvot.imag, "o", color=KOROSTUS,
                markersize=3.2 if bitteja < 6 else 2, zorder=2)
        if bitteja <= 4:
            for avain, p in pisteet.items():
                ax.text(p.real, p.imag + 0.13, f"{avain:0{bitteja}b}",
                        ha="center", family=MONO, fontsize=5.5, zorder=3)
        ax.axhline(0, color=HARMAA, linewidth=0.5, zorder=0)
        ax.axvline(0, color=HARMAA, linewidth=0.5, zorder=0)
        ax.set_aspect("equal")
        ax.set(xlim=(-1.6, 1.6), ylim=(-1.6, 1.6), xticks=[], yticks=[],
               title=f"{nimi}: {bitteja} bittiä/symboli")
        ax.title.set_fontsize(8)
        for sivu in ("left", "bottom"):
            ax.spines[sivu].set_visible(False)
    akselit[0].set_xlabel("I (kosinikomponentti)", fontsize=7)
    akselit[0].set_ylabel("Q (sinikomponentti)", fontsize=7)
    tallenna(fig, polku)


# --- Luku 5: lomitus ja ARQ ------------------------------------------------

def lomitus(polku: Path) -> None:
    m = lataa("05-lomitus.py")
    n = m.RIVEJA * m.SARAKKEITA
    varit = [KOROSTUS_VAALEA, TOINEN_VAALEA, KOLMAS_VAALEA, "#E8D5E0"]
    reunat = [KOROSTUS, TOINEN, KOLMAS, "#A14B7C"]
    fig = uusi(5.8, 1.9)
    ax = fig.add_subplot()
    ax.set_axis_off()
    ax.set(xlim=(-0.3, n + 0.3), ylim=(-0.6, 4.3))
    jarjestykset = [
        (2.6, list(range(n)), "lähetysjärjestys ilman lomitusta"),
        (0.2, m.lomita(list(range(n))), "lähetysjärjestys lomitettuna"),
    ]
    for y, jarjestys, otsikko in jarjestykset:
        ax.text(0, y + 1.15, otsikko, fontsize=8)
        for i, alkuperainen in enumerate(jarjestys):
            sana = alkuperainen // m.SARAKKEITA
            osuma = 10 <= i < 14
            ax.add_patch(Rectangle((i, y), 1, 0.9, facecolor=varit[sana],
                                   edgecolor=reunat[sana], linewidth=0.6))
            ax.text(i + 0.5, y + 0.45, str(sana + 1), ha="center",
                    va="center", fontsize=7,
                    fontweight="bold" if osuma else "normal")
            if osuma:
                ax.plot([i + 0.12, i + 0.88], [y + 0.1, y + 0.8],
                        color=PUNAINEN, linewidth=1.2)
                ax.plot([i + 0.12, i + 0.88], [y + 0.8, y + 0.1],
                        color=PUNAINEN, linewidth=1.2)
    ax.plot([10, 14], [-0.25, -0.25], color=PUNAINEN, linewidth=1.5)
    ax.text(12, -0.42, "neljän bitin purske", ha="center", va="top",
            fontsize=7, color=PUNAINEN)
    ax.text(n, 4.05, "numero = koodisana", ha="right", fontsize=7,
            color=HARMAA)
    tallenna(fig, polku)


def arq(polku: Path) -> None:
    m = lataa("05-arq.py")
    kierros = 20
    fig = uusi(4.6, 2.7)
    ax = fig.add_subplot()
    p = np.logspace(-3, np.log10(0.3), 100)
    ax.semilogx(p, 1 - p, color=KOLMAS, label="valikoiva toisto")
    ax.semilogx(p, (1 - p) / (1 + kierros * p), color=KOROSTUS,
                label="go-back-N")
    ax.semilogx(p, (1 - p) / (1 + kierros), color=TOINEN,
                label="pysähdy ja odota")
    for q in (0.003, 0.01, 0.03, 0.1, 0.25):
        katoaa = m.kanava(q, 100_000)
        ax.plot([q], [m.valikoiva_toisto(katoaa, kierros)[0]], "o",
                color=KOLMAS, markersize=3.5)
        ax.plot([q], [m.palaa_n(katoaa, kierros)], "o", color=KOROSTUS,
                markersize=3.5)
        ax.plot([q], [m.pysahdy_ja_odota(katoaa, kierros)], "o",
                color=TOINEN, markersize=3.5)
    ax.set(xlabel="kehyksen katoamistodennäköisyys p",
           ylabel="tehokkuus", ylim=(0, 1.05), xlim=(1e-3, 0.3))
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.42))
    ax.grid(True)
    tallenna(fig, polku)


# --- Luku 6: kanavointi ja OFDM ---------------------------------------------

def kanavointi(polku: Path) -> None:
    varit = [KOROSTUS, TOINEN, KOLMAS]
    fig = uusi(5.8, 2.1)
    akselit = fig.subplots(1, 3)
    for ax, otsikko in zip(akselit, ("TDM", "FDM", "OFDMA"), strict=True):
        ax.set(xlim=(0, 6), ylim=(0, 6), xticks=[], yticks=[], title=otsikko)
        ax.title.set_fontsize(8.5)
        ax.set_xlabel("aika", fontsize=7.5)
    akselit[0].set_ylabel("taajuus", fontsize=7.5)
    for k in range(6):                                    # TDM
        akselit[0].add_patch(Rectangle((k + 0.04, 0.04), 0.92, 5.92,
                                       facecolor=varit[k % 3], alpha=0.8))
        akselit[0].text(k + 0.5, 3, "ABC"[k % 3], ha="center", va="center",
                        color="white", fontsize=8, fontweight="bold")
    for k in range(3):                                    # FDM
        akselit[1].add_patch(Rectangle((0.04, 2 * k + 0.2), 5.92, 1.6,
                                       facecolor=varit[k], alpha=0.8))
        akselit[1].text(3, 2 * k + 1, "ABC"[k], ha="center", va="center",
                        color="white", fontsize=8, fontweight="bold")
    akselit[1].text(3, 2.0, "suojakaista", ha="center", va="center",
                    fontsize=5.5, color=HARMAA)
    jako = ["AAABBC", "AABBBC", "CCABBB", "CAAABB", "BBAACC", "BBBACC"]
    for y, rivi in enumerate(jako):                       # OFDMA
        for x, kayttaja in enumerate(rivi):
            akselit[2].add_patch(Rectangle(
                (x + 0.04, y + 0.04), 0.92, 0.92,
                facecolor=varit["ABC".index(kayttaja)], alpha=0.8))
            akselit[2].text(x + 0.5, y + 0.5, kayttaja, ha="center",
                            va="center", color="white", fontsize=6.5)
    tallenna(fig, polku)


def ofdm(polku: Path) -> None:
    m = lataa("06-ofdm.py")
    fig = uusi(5.8, 2.3)
    ax1, ax2 = fig.subplots(1, 2, width_ratios=[1, 1.15])
    f = np.linspace(-3.5, 3.5, 700)
    for k in (-2, -1, 0, 1, 2):
        vari = KOROSTUS if k == 0 else VAALEA
        ax1.plot(f, np.sinc(f - k), color=vari,
                 linewidth=1.4 if k == 0 else 0.9, zorder=3 if k == 0 else 2)
        ax1.plot([k], [1], "o", color=vari, markersize=3, zorder=4)
        ax1.axvline(k, color=HAALEA, linewidth=0.7, zorder=0)
    ax1.axhline(0, color=HARMAA, linewidth=0.5)
    ax1.set(xlabel="taajuus (alikantoaaltoväliä)", yticks=[],
            title="Alikantoaaltojen spektrit", xlim=(-3.5, 3.5))
    ax1.title.set_fontsize(8.5)
    ax1.spines["left"].set_visible(False)
    rng = np.random.default_rng(6)
    taajuustaso = np.zeros(m.ALIKANTOJA, dtype=complex)
    taajuustaso[1:6] = m.qpsk(rng.integers(0, 2, 10))
    symboli = np.fft.ifft(taajuustaso).real
    lahetys = np.concatenate([symboli[-m.ETULIITE:], symboli])
    n = np.arange(len(lahetys))
    ax2.axvspan(0, m.ETULIITE, color=TOINEN_VAALEA)
    ax2.axvspan(len(lahetys) - m.ETULIITE, len(lahetys),
                color=TOINEN_VAALEA)
    ax2.plot(n, lahetys, color=KOROSTUS, linewidth=1.1)
    huippu = float(np.abs(lahetys).max())
    ax2.annotate("", (m.ETULIITE / 2, huippu * 1.25),
                 (len(lahetys) - m.ETULIITE / 2, huippu * 1.25),
                 arrowprops={"arrowstyle": "->", "color": TOINEN,
                             "connectionstyle": "arc3,rad=0.12",
                             "linewidth": 0.9})
    ax2.text(len(lahetys) / 2, huippu * 1.72, "loppuosan kopio",
             ha="center", fontsize=7, color=TOINEN)
    ax2.text(m.ETULIITE / 2, -huippu * 1.5, "etuliite", ha="center",
             fontsize=7, color=TOINEN)
    ax2.set(xlabel="näyte", yticks=[], title="Symboli ja syklinen etuliite",
            xlim=(0, len(lahetys)), ylim=(-huippu * 1.7, huippu * 2.1))
    ax2.set_xticks([0, m.ETULIITE, len(lahetys)])
    ax2.title.set_fontsize(8.5)
    ax2.spines["left"].set_visible(False)
    tallenna(fig, polku)


# --- Luku 7: viiveen osat ----------------------------------------------------

def viive(polku: Path) -> None:
    """Periaatekuva: paketti lähettäjältä reitittimen kautta perille.
    Aika kulkee alaspäin; mittakaava on havainnollinen."""
    fig = uusi(4.8, 3.0)
    ax = fig.add_subplot()
    ax.set_axis_off()
    ax.set(xlim=(-2.6, 9.2), ylim=(9.8, -1.0))
    solmut = [(0, "lähettäjä"), (4, "reititin"), (8, "vastaanottaja")]
    for x, nimi in solmut:
        ax.plot([x, x], [0, 9.5], color=VAALEA, linewidth=1)
        ax.text(x, -0.35, nimi, ha="center", fontsize=8)
    siirto1, etene1, kasittely, jono, siirto2, etene2 = (1.6, 1.2, 0.4, 1.3,
                                                         0.8, 2.0)
    t0 = 0.3
    ax.add_patch(Polygon([(0, t0), (4, t0 + etene1),
                          (4, t0 + etene1 + siirto1), (0, t0 + siirto1)],
                         facecolor=KOROSTUS_VAALEA, edgecolor=KOROSTUS,
                         linewidth=0.9))
    t1 = t0 + etene1 + siirto1 + kasittely + jono
    ax.add_patch(Polygon([(4, t1), (8, t1 + etene2),
                          (8, t1 + etene2 + siirto2), (4, t1 + siirto2)],
                         facecolor=KOROSTUS_VAALEA, edgecolor=KOROSTUS,
                         linewidth=0.9))
    ax.add_patch(Rectangle((3.85, t0 + etene1 + siirto1), 0.3, kasittely,
                           facecolor=TOINEN, edgecolor="none"))
    ax.add_patch(Rectangle((3.85, t0 + etene1 + siirto1 + kasittely), 0.3,
                           jono, facecolor=TOINEN_VAALEA, edgecolor=TOINEN,
                           linewidth=0.6))

    def mitta(x: float, y0: float, y1: float, teksti: str,
              puoli: str = "right") -> None:
        ax.annotate("", (x, y0), (x, y1),
                    arrowprops={"arrowstyle": "<->", "color": HARMAA,
                                "linewidth": 0.6, "shrinkA": 0,
                                "shrinkB": 0})
        ax.text(x - 0.15 if puoli == "right" else x + 0.15, (y0 + y1) / 2,
                teksti, ha=puoli, va="center", fontsize=7, color=MUSTE)

    mitta(-0.3, t0, t0 + siirto1, "siirtoviive:\nensimmäisestä bitistä\n"
          "viimeiseen")
    mitta(4.45, t0, t0 + etene1, "etenemisviive", "left")
    ax.plot([0, 4.45], [t0, t0], color=VAALEA, linewidth=0.5,
            linestyle=":")
    ax.text(4.3, t0 + etene1 + siirto1 + kasittely / 2, "käsittely",
            va="center", fontsize=7)
    ax.text(4.3, t0 + etene1 + siirto1 + kasittely + jono / 2,
            "jonoviive: linkki\non varattu", va="center", fontsize=7)
    ax.text(6.25, t1 + 0.45, "nopeampi linkki:\nlyhyempi siirtoviive",
            fontsize=6.5, color=HARMAA, ha="left", va="center")
    ax.annotate("", (-2.3, 9.3), (-2.3, 0.3),
                arrowprops={"arrowstyle": "->", "color": HARMAA,
                            "linewidth": 0.7})
    ax.text(-2.15, 9.2, "aika", fontsize=7, color=HARMAA, va="bottom")
    tallenna(fig, polku)


# --- Luku 8: ALOHA ja piilotettu asema ------------------------------------------

def aloha(polku: Path) -> None:
    m = lataa("08-aloha.py")
    fig = uusi(4.6, 2.7)
    ax = fig.add_subplot()
    g = np.linspace(0.001, 3, 300)
    ax.plot(g, g * np.exp(-g), color=KOROSTUS, label="viipaloitu ALOHA")
    ax.plot(g, g * np.exp(-2 * g), color=TOINEN, label="puhdas ALOHA")
    for kuorma in (0.25, 0.5, 1.0, 1.5, 2.0, 2.5):
        ax.plot([kuorma], [m.viipaloitu(kuorma, viipaleita=50_000)], "o",
                color=KOROSTUS, markersize=3.5)
        ax.plot([kuorma], [m.puhdas(kuorma, kehyksia=50_000)], "o",
                color=TOINEN, markersize=3.5)
    ax.annotate("1/e ≈ 0,37", (1, 1 / math.e), (1.25, 0.39), fontsize=7)
    ax.annotate("1/(2e) ≈ 0,18", (0.5, 1 / (2 * math.e)), (0.75, 0.215),
                fontsize=7)
    ax.set(xlabel="kuorma G (yritystä kehysaikaa kohti)",
           ylabel="läpäisy S", xlim=(0, 3), ylim=(0, 0.45))
    ax.legend(loc="upper right")
    ax.grid(True)
    tallenna(fig, polku)


def piilotettu(polku: Path) -> None:
    fig = uusi(4.8, 2.9)
    ax = fig.add_subplot()
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.set(xlim=(-3.3, 3.3), ylim=(-1.95, 1.95))
    for x, vari, tausta in ((-1.25, KOROSTUS, KOROSTUS_VAALEA),
                            (1.25, TOINEN, TOINEN_VAALEA)):
        ax.add_patch(Circle((x, 0), 1.75, facecolor=tausta, alpha=0.45,
                            edgecolor=vari, linestyle="--", linewidth=0.8))
    for x, nimi, vari in ((-1.25, "asema A", KOROSTUS),
                          (0, "tukiasema", MUSTE),
                          (1.25, "asema C", TOINEN)):
        ax.plot([x], [0], "o", color=vari, markersize=6)
        ax.text(x, -0.32, nimi, ha="center", fontsize=7.5)
    nuolet = [((-1.1, 0.45), (-0.12, 0.45), "1. RTS", KOROSTUS),
              ((-0.12, 0.85), (-1.1, 0.85), "2. CTS", MUSTE),
              ((0.12, 0.85), (1.1, 0.85), "2. CTS", MUSTE)]
    for alku, loppu, teksti, vari in nuolet:
        ax.annotate("", loppu, alku,
                    arrowprops={"arrowstyle": "->", "color": vari,
                                "linewidth": 1})
        ax.text((alku[0] + loppu[0]) / 2, alku[1] + 0.08, teksti,
                ha="center", fontsize=7, color=vari)
    ax.text(-2.55, -1.2, "A:n kantama", fontsize=7, color=KOROSTUS,
            ha="center")
    ax.text(2.55, -1.2, "C:n kantama", fontsize=7, color=TOINEN,
            ha="center")
    ax.text(1.25, 0.28, "C ei kuule A:ta,\nmutta kuulee CTS:n",
            ha="center", fontsize=6.5, color=HARMAA)
    tallenna(fig, polku)


# --- Luku 10: solut ---------------------------------------------------------------

def solut(polku: Path) -> None:
    """Kuusikulmioruudukot samoilla aksiaalisilla koordinaateilla kuin
    esimerkin 10-solut.py funktiossa tukiasemat."""
    fig = uusi(5.8, 2.3)
    akselit = fig.subplots(1, 3)
    savyt = [KOROSTUS, "#E7ECEF", "#D3DCE1", "#F3E9D8", "#DCEBDA",
             "#EFDDE7", "#E4E0F0"]
    ryhmat = {1: lambda q, r: 0, 3: lambda q, r: (q - r) % 3,
              7: lambda q, r: (q - 2 * r) % 7}
    kehia = 3
    for ax, n in zip(akselit, (1, 3, 7), strict=True):
        for q in range(-kehia, kehia + 1):
            for r in range(max(-kehia, -q - kehia),
                           min(kehia, -q + kehia) + 1):
                x = math.sqrt(3) * (q + r / 2)
                y = 1.5 * r
                ryhma = ryhmat[n](q, r)
                kulmat = [(x + math.cos(math.radians(60 * k + 30)),
                           y + math.sin(math.radians(60 * k + 30)))
                          for k in range(6)]
                ax.add_patch(Polygon(kulmat, facecolor=savyt[ryhma],
                                     edgecolor="white", linewidth=0.8))
                ax.text(x, y, str(ryhma + 1), ha="center", va="center",
                        fontsize=6,
                        color="white" if ryhma == 0 else HARMAA)
        ax.set_aspect("equal")
        ax.set(xlim=(-6.3, 6.3), ylim=(-5.7, 5.7))
        ax.set_axis_off()
        ax.set_title(f"N = {n}", fontsize=8.5)
    tallenna(fig, polku)


# --- Luku 11: jonot ------------------------------------------------------------------

def mm1(polku: Path) -> None:
    m = lataa("11-mm1.py")
    fig = uusi(4.6, 2.7)
    ax = fig.add_subplot()
    rho = np.linspace(0, 0.97, 300)
    ax.plot(rho, 1 / (1 - rho), color=KOROSTUS, label="W = 1/(μ − λ)")
    for kuorma in (0.3, 0.5, 0.7, 0.8, 0.9, 0.95):
        w, _ = m.simuloi(kuorma, 100_000)
        ax.plot([kuorma], [w], "o", color=TOINEN, markersize=3.5,
                label="simulaatio" if kuorma == 0.3 else None)
    for kuorma in (0.5, 0.9):
        ax.annotate(f"ρ = {kuorma}: {1 / (1 - kuorma):.0f}".replace(".", ","),
                    (kuorma, 1 / (1 - kuorma)),
                    (kuorma - 0.27, 1 / (1 - kuorma) + 4), fontsize=7,
                    arrowprops={"arrowstyle": "-", "color": HARMAA,
                                "linewidth": 0.5})
    ax.set(xlabel="kuormitus ρ", xlim=(0, 1), ylim=(0, 32),
           ylabel="aika järjestelmässä (palveluaikoina)")
    ax.legend(loc="upper left")
    ax.grid(True)
    tallenna(fig, polku)


def ampari(polku: Path) -> None:
    m = lataa("11-token-bucket.py")
    fig = uusi(5.8, 2.3)
    ax1, ax2 = fig.subplots(1, 2, sharey=True)
    b = m.Ampari(nopeus=125_000, koko=15_000)
    tapahtumat = []
    for t, koko in m.saapumiset:
        ok = b.salli(t, koko)
        tapahtumat.append((t, b.rahakkeita, ok))
    for ax, osa, otsikko, kerroin, yksikko in (
            (ax1, tapahtumat[:20], "Purske: 20 pakettia 2 ms:ssa", 1e3,
             "aika (ms)"),
            (ax2, tapahtumat[20:], "Tasainen virta 0,8 Mbit/s", 1e3,
             "aika (ms)")):
        ajat = [t * kerroin for t, _, _ in osa]
        ax.step(ajat, [r / 1500 for _, r, _ in osa], where="post",
                color=KOROSTUS, linewidth=1.1)
        for (_, r, ok), x in zip(osa, ajat, strict=True):
            ax.plot([x], [r / 1500], "o" if ok else "x",
                    color=KOLMAS if ok else PUNAINEN, markersize=3.5)
        ax.set(xlabel=yksikko, title=otsikko, ylim=(-0.6, 10.8))
        ax.title.set_fontsize(8.5)
        ax.grid(True)
    ax1.set_ylabel("rahakkeita ämpärissä\n(paketteina)")
    ax1.plot([], [], "o", color=KOLMAS, markersize=3.5, label="hyväksytty")
    ax1.plot([], [], "x", color=PUNAINEN, markersize=3.5, label="hylätty")
    ax1.legend(loc="upper right")
    tallenna(fig, polku)


KUVAT = {
    "kupari": kupari, "radio": radio, "shannon": shannon, "linjakoodit": linjakoodit,
    "pam4": pam4, "konstellaatio": konstellaatio, "lomitus": lomitus,
    "arq": arq, "kanavointi": kanavointi, "ofdm": ofdm, "viive": viive,
    "aloha": aloha, "piilotettu": piilotettu, "solut": solut, "mm1": mm1,
    "ampari": ampari,
}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    valitut = sys.argv[2:] or list(KUVAT)
    for kuva in valitut:
        KUVAT[kuva](kohde / f"{kuva}.png")
