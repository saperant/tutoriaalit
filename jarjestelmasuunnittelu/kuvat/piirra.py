"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
lukujen testattujen esimerkkien funktioilla ja vakioilla samoilla
siemenillä, joten kuvat näyttävät samat ajot kuin tulosteet.
"""

import importlib.util
import math
import random
import sys
from pathlib import Path
from types import ModuleType

from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import Patch, Wedge

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))

from jarjestelma.hajautus import Rengas, tiiviste

KOROSTUS = "#546676"
TOINEN = "#B07A2A"
VIRHE = "#B4532A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
TUMMA = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def lataa(polku: str) -> ModuleType:
    """Lataa esimerkin moduulina ajamatta sen main-funktiota."""
    tiedosto = ESIMERKIT / polku
    spec = importlib.util.spec_from_file_location(
        tiedosto.stem + "_kuva", tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(moduuli)
    return moduuli


def uusi(leveys: float = 4.6, korkeus: float = 2.7) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def hanta(polku: Path) -> None:
    """Latenssin häntä: osuus pyynnöistä, jotka ylittävät keston."""
    m = lataa("luku03/hantalatenssi.py")
    s = random.Random(2026)            # sama järjestys kuin esimerkissä
    sarjat = []
    for n in (1, 10, 100):
        sarjat.append((f"{n} taustakutsu" + ("" if n == 1 else "a"),
                       [m.hajautettu(s, n) for _ in range(m.PYYNTOJA)]))
    varmistettu = [m.varmistettu(s, 10, 20) for _ in range(m.PYYNTOJA)]
    fig = uusi()
    ax = fig.add_subplot()
    tyylit = [(VAALEA, 0.0135), (HARMAA, 0.125), (TUMMA, 0.8)]
    for (nimi, arvot), (vari, korkeus) in zip(sarjat, tyylit, strict=True):
        x = sorted(arvot)
        y = [1 - i / len(x) for i in range(len(x))]
        ax.step(x, y, where="post", color=vari, linewidth=1.3)
        ax.text(60, korkeus, nimi, fontsize=7.5, va="bottom",
                color=HARMAA if vari == VAALEA else vari)
    x = sorted(varmistettu)
    ax.step(x, [1 - i / len(x) for i in range(len(x))], where="post",
            color=TOINEN, linestyle="--", linewidth=1.3)
    ax.text(40, 0.0011, "10 kutsua, varmistus 20 ms", fontsize=7.5,
            va="bottom", color=TOINEN)
    ax.axhline(0.01, color=HARMAA, linewidth=0.5, linestyle=":")
    ax.text(302, 0.0115, "p99", fontsize=7, color=HARMAA, ha="right")
    ax.set_yscale("log")
    ax.set(xlabel="pyynnön kesto (ms)", ylabel="hitaampien osuus",
           xlim=(0, 305), ylim=(1e-4, 1.3))
    ax.set_yticks([1, 0.1, 0.01, 0.001, 0.0001],
                  ["100 %", "10 %", "1 %", "0,1 %", "0,01 %"])
    tallenna(fig, polku)


def kayttoaste(polku: Path) -> None:
    """Jonotusaika käyttöasteen funktiona, kun käsittelijöitä on c."""
    m = lataa("luku03/kapasiteetti.py")
    fig = uusi()
    ax = fig.add_subplot()
    asteet = [i / 1000 for i in range(300, 991)]
    for c, vari, viiva in ((1, VAALEA, "-"), (8, TOINEN, "--"),
                           (56, KOROSTUS, "-")):
        y = [m.erlang_c(c, r * c) / (c - r * c) for r in asteet]
        ax.plot([100 * r for r in asteet], y, color=vari, linewidth=1.4,
                linestyle=viiva,
                label=f"{c} käsittelijä" + ("" if c == 1 else "ä"))
    aste = m.KUORMA * m.PALVELUAIKA / 56
    ax.plot([100 * aste], [m.erlang_c(56, 48) / 8], "o", color=KOROSTUS,
            markersize=4)
    ax.annotate("7 palvelinta,\n86 %", (100 * aste, m.erlang_c(56, 48) / 8),
                (72, 1.2), fontsize=7.5, color=KOROSTUS,
                arrowprops={"arrowstyle": "-", "color": KOROSTUS,
                            "linewidth": 0.6})
    ax.set(xlabel="käyttöaste (%)",
           ylabel="jonotus / palveluaika", xlim=(30, 100), ylim=(0, 6.5))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    tallenna(fig, polku)


def tasaus(polku: Path) -> None:
    """Kuormantasausalgoritmit: hitaan palvelimen osuus ja p99."""
    m = lataa("luku04/algoritmit.py")
    strategiat = [("kierto", lambda s: m.kierto()),
                  ("satunnainen", m.satunnainen),
                  ("painotettu kierto", lambda s: m.painotettu_kierto()),
                  ("vähiten kesken", lambda s: m.vahiten_kesken()),
                  ("kaksi satunnaista", m.kaksi_satunnaista)]
    nimet, p99t, osuudet = [], [], []
    for nimi, tee in strategiat:
        s = random.Random(42)
        _, p99, osuus = m.simuloi(tee(s), s)
        nimet.append(nimi)
        p99t.append(p99)
        osuudet.append(100 * osuus)
    fig = uusi(5.4, 2.3)
    vasen, oikea = fig.subplots(1, 2, sharey=True)
    paikat = list(range(len(nimet)))[::-1]
    kestaa = 100 * m.NOPEUDET[-1] / sum(m.NOPEUDET) / 0.75
    varit = [VIRHE if o > kestaa else KOROSTUS for o in osuudet]
    vasen.barh(paikat, osuudet, color=varit, height=0.6)
    vasen.axvline(kestaa, color=HARMAA, linewidth=0.6, linestyle=":")
    vasen.text(kestaa + 0.4, -0.75, "hitaan kapasiteetti", fontsize=6.5,
               color=HARMAA, va="top")
    vasen.set_yticks(paikat, nimet)
    vasen.set(xlabel="hitaalle palvelimelle (%)", xlim=(0, 30),
              ylim=(-1.3, 4.5))
    oikea.barh(paikat, p99t, color=varit, height=0.6)
    oikea.set_xscale("log")
    oikea.set(xlabel="p99 (ms, logaritminen)", xlim=(10, 2e5))
    for ax in (vasen, oikea):
        ax.tick_params(axis="y", length=0)
    tallenna(fig, polku)


def rengas(polku: Path) -> None:
    """Hajautusrengas ennen ja jälkeen viidennen solmun lisäämisen."""
    virtuaaleja = 4
    solmut = ["s1", "s2", "s3", "s4"]
    varit = {"s1": "#DCE3E8", "s2": "#B8C4C8", "s3": "#8A9AA3",
             "s4": "#5B6B70", "s5": TOINEN}

    def kaaret(nimet: list[str]) -> list[tuple[float, float, str]]:
        r = Rengas(nimet, virtuaaleja)
        pisteet = sorted((tiiviste(f"{s}#{i}") / 2 ** 64, s)
                         for s in nimet for i in range(virtuaaleja))
        assert r.solmu("x") in nimet
        tulos = []
        edellinen = pisteet[-1][0] - 1.0
        for paikka, solmu in pisteet:   # kaari kuuluu päätepisteelleen
            tulos.append((edellinen, paikka, solmu))
            edellinen = paikka
        return tulos

    fig = uusi(5.2, 2.7)
    akselit = fig.subplots(1, 2)
    for ax, nimet, otsikko in ((akselit[0], solmut, "neljä solmua"),
                               (akselit[1], [*solmut, "s5"],
                                "s5 lisätty")):
        for alku, loppu, solmu in kaaret(nimet):
            # Kulma 0 on ylhäällä ja kasvaa myötäpäivään.
            ax.add_patch(Wedge((0, 0), 1.0, 90 - 360 * loppu,
                               90 - 360 * alku, width=0.28,
                               facecolor=varit[solmu], edgecolor="white",
                               linewidth=0.8))
            kulma = math.radians(90 - 360 * loppu)
            ax.plot([math.cos(kulma)], [math.sin(kulma)], "o",
                    color="#1F2A2E", markersize=2.2)
        ax.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1), aspect="equal")
        ax.axis("off")
        ax.set_title(otsikko, fontsize=9)
    fig.legend(handles=[Patch(facecolor=v, label=s) for s, v in varit.items()],
               loc="outside lower center", ncols=5, frameon=False,
               fontsize=7.5, handlelength=1.2)
    tallenna(fig, polku)


def jono(polku: Path) -> None:
    """Kampanjan purske: saapuva kuorma, kapasiteetti ja jonon pituus."""
    m = lataa("luku08/tasaus.py")
    minuutit = list(range(101))
    saapuu, pituus = [], [0]
    jonossa = 0
    for minuutti in range(100):        # sama malli kuin esimerkissä
        tulo = m.PURSKE if minuutti in m.KAMPANJA else m.PERUS
        saapuu.append(tulo)
        jonossa = max(0, jonossa + (tulo - m.KAPASITEETTI) * 60)
        pituus.append(jonossa)
    fig = uusi(4.8, 3.0)
    yla, ala = fig.subplots(2, 1, sharex=True,
                            gridspec_kw={"height_ratios": [1, 1.3]})
    yla.step(minuutit, [*saapuu, saapuu[-1]], where="post",
             color=KOROSTUS, linewidth=1.3, label="saapuu")
    yla.axhline(m.KAPASITEETTI, color=TOINEN, linewidth=1, linestyle="--",
                label="käsittelykapasiteetti")
    yla.set(ylabel="tilausta/s", ylim=(0, 230))
    yla.legend(frameon=False, fontsize=7.5, loc="upper right")
    ala.fill_between(minuutit, [p / 1000 for p in pituus], color=VAALEA,
                     linewidth=0)
    ala.plot(minuutit, [p / 1000 for p in pituus], color=HARMAA,
             linewidth=1.3)
    ala.set(xlabel="aika (min)", ylabel="jonossa (tuhatta)",
            xlim=(0, 100), ylim=(0, 120))
    tallenna(fig, polku)


def myrsky(polku: Path) -> None:
    """Uudelleenyritysmyrsky: onnistuneet vastaukset kolmella tavalla."""
    m = lataa("luku09/myrsky.py")
    fig = uusi(4.8, 2.6)
    ax = fig.add_subplot()
    ax.axvspan(*m.HAIRIO, color="#EEF1F3", linewidth=0)
    ax.text(sum(m.HAIRIO) / 2, 108, "kapasiteetti\npuolittuu", fontsize=7,
            color=HARMAA, ha="center", va="top")
    ajat = [5 * i for i in range(13)]
    for strategia, vari, viiva in (("naiivi", VIRHE, "-"),
                                   ("budjetti", TOINEN, "--"),
                                   ("määräaika", KOROSTUS, "-")):
        y = m.simuloi(strategia)
        ax.step(ajat, [*y, y[-1]], where="post", color=vari,
                linestyle=viiva, linewidth=1.4, label=strategia)
    ax.axhline(m.KUORMA, color=HARMAA, linewidth=0.5, linestyle=":")
    ax.set(xlabel="aika (s)", ylabel="onnistuneita vastauksia/s",
           xlim=(0, 60), ylim=(0, 110))
    ax.legend(frameon=False, fontsize=7.5, loc="lower right",
              bbox_to_anchor=(1.0, 0.12))
    tallenna(fig, polku)


KUVAT = {"hanta": hanta, "kayttoaste": kayttoaste, "tasaus": tasaus,
         "rengas": rengas, "jono": jono, "myrsky": myrsky}


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"kuvat/{nimi}.png")


if __name__ == "__main__":
    main()
