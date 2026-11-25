"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE [NIMI…]

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Jokainen kuva
lasketaan lukujen testattujen esimerkkien funktioilla: esimerkki ladataan
moduulina ja sen tulostus ohitetaan.
"""

import contextlib
import importlib.util
import io
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT / "03-kuljetus"))
sys.path.insert(0, str(ESIMERKIT / "07-virta"))

KOROSTUS = "#9A6524"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
SININEN = "#2F6B8A"
KARTTA = LinearSegmentedColormap.from_list(
    "lampo", ["#243B53", "#5B8FA8", "#F3EBDD", "#D08A3C", "#7A2E12"])
SAVU = LinearSegmentedColormap.from_list(
    "savu", ["#FFFFFF", "#D9C7A8", "#9A6524", "#4A2A0C"])
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 4.4, korkeus: float = 2.8, dpi: int = 200) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=dpi, layout="constrained")


def lataa(tiedosto: str) -> ModuleType:
    """Lataa esimerkkiohjelman moduulina; sen tulosteet ohitetaan."""
    nimi = "esimerkki_" + tiedosto.removesuffix(".py").replace(
        "-", "_").replace("/", "_")
    if nimi in sys.modules:
        return sys.modules[nimi]
    spec = importlib.util.spec_from_file_location(nimi, ESIMERKIT / tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    sys.modules[nimi] = moduuli
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(moduuli)
    return moduuli


def virtaviivat(ax: Axes, teht: Any, tila: Any, tasoja: int = 16,
                vari: str = HARMAA) -> None:
    from virta import virtafunktio
    psi = virtafunktio(teht, tila.u)
    x = np.linspace(0.0, teht.lx, teht.nx + 1)
    y = np.linspace(0.0, teht.ly, teht.ny + 1)
    ax.contour(x, y, psi.T, levels=tasoja, colors=vari, linewidths=0.6,
               linestyles="solid")


# --- Luku 1 -------------------------------------------------------------

def levy(polku: Path) -> None:
    m = lataa("01-levy.py")
    fig = uusi()
    ax = fig.add_subplot()
    tihea = np.linspace(0.0, 0.006, 200)
    for t, vari in ((0.1, VAALEA), (0.3, HARMAA), (1.0, "black")):
        ax.plot(m.tarkka(tihea, t), 1e3 * tihea, color=vari, linewidth=1.2,
                label=f"tarkka, t = {t:g} s".replace(".", ","))
    y, u = m.ratkaise(50, 25)
    ax.plot(u[:15], 1e3 * y[:15], "o", color=KOROSTUS, markersize=3.5,
            label="laskettu, t = 1 s")
    ax.set(xlabel="nopeus (m/s)", ylabel="etäisyys levystä (mm)",
           ylim=(0, 6))
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


# --- Luku 2 -------------------------------------------------------------

def voitelukalvo(polku: Path) -> None:
    m = lataa("02-kanava.py")
    fig = uusi()
    ax = fig.add_subplot()
    tihea = np.linspace(0.0, m.RAKO, 120)
    for nimi, mu, vari in (("vakioviskositeetti", m.vakio, HARMAA),
                           ("lämpenevä öljy", m.lampeneva, KOROSTUS)):
        ax.plot([m.tarkka(float(s), mu) for s in tihea], 1e6 * tihea,
                color=vari, linewidth=1.2, label=nimi)
        y, u, _ = m.ratkaise(10, mu)
        ax.plot(u, 1e6 * y, "o", color=vari, markersize=3.5)
    ax.plot([], [], "o", color="black", markersize=3.5,
            label="10 kontrollitilavuutta")
    ax.axhline(0, color="black", linewidth=1.5)
    ax.axhline(1e6 * m.RAKO, color="black", linewidth=1.5)
    ax.text(0.1, 1.5, "liikkuva levy, 5 m/s", fontsize=8, color=HARMAA)
    ax.text(3.6, 45.0, "paikallaan oleva levy", fontsize=8, color=HARMAA)
    ax.set(xlabel="nopeus (m/s)", ylabel="korkeus raossa (µm)")
    ax.legend(frameon=False, fontsize=8, loc="center left",
              bbox_to_anchor=(0.0, 0.42))
    tallenna(fig, polku)


# --- Luku 3 -------------------------------------------------------------

def tilavuus(polku: Path) -> None:
    """Periaatekuva: kontrollitilavuus ja sen pintojen vuot."""
    fig = uusi(4.4, 2.3)
    ax = fig.add_subplot()
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((i, j), 1, 1, fill=False,
                                   edgecolor=VAALEA, linewidth=0.8))
            ax.plot(i + 0.5, j + 0.5, "o", color=VAALEA, markersize=3)
    ax.add_patch(Rectangle((1, 1), 1, 1, facecolor="#F3EBDD",
                           edgecolor=KOROSTUS, linewidth=1.5))
    ax.plot(1.5, 1.5, "o", color=KOROSTUS, markersize=5)
    ax.text(1.5, 1.32, "P", ha="center", fontsize=9, color=KOROSTUS)
    for (x, y, dx, dy, nimi, tx, ty) in (
            (0.72, 1.5, 0.5, 0, "länsi", 0.5, 1.62),
            (1.78, 1.5, 0.5, 0, "itä", 2.5, 1.62),
            (1.5, 0.72, 0, 0.5, "etelä", 1.83, 0.86),
            (1.5, 1.78, 0, 0.5, "pohjoinen", 1.93, 2.12)):
        ax.annotate("", (x + dx, y + dy), (x, y),
                    arrowprops={"arrowstyle": "->", "color": SININEN,
                                "linewidth": 1.3})
        ax.text(tx, ty, nimi, ha="center", fontsize=7.5, color=SININEN)
    ax.text(3.25, 2.2, "ruudun P tase:", fontsize=8.5)
    ax.text(3.25, 1.8, "muutos = sisään − ulos + lähde", fontsize=8.5)
    ax.text(3.25, 1.2, "Pinnan vuo lasketaan kerran:\nse lähtee yhdestä "
            "ruudusta\nja saapuu naapuriin.", fontsize=8, color=HARMAA)
    ax.set(xlim=(-0.1, 6.2), ylim=(-0.1, 3.1), aspect="equal")
    ax.axis("off")
    tallenna(fig, polku)


def sailyvyys(polku: Path) -> None:
    m = lataa("03-sailyvyys.py")
    a, b, maarat = m.aja()
    fig = uusi(5.6, 2.5)
    vasen, oikea = fig.subplots(1, 2)
    x = m.KESKET
    vasen.plot(x, m.alkutila(), color=VAALEA, linewidth=1.2, label="alku")
    vasen.plot(x, a, color=KOROSTUS, linewidth=1.2, label="säilyvä")
    vasen.plot(x, b, color=SININEN, linewidth=1.2, linestyle="--",
               label="auki kerrottu")
    nopeus = vasen.twinx()
    nopeus.plot(m.PINNAT, m.nopeus(m.PINNAT), color=HARMAA, linewidth=0.8,
                linestyle=":")
    nopeus.set_ylabel("virtausnopeus (pisteviiva)", fontsize=8)
    nopeus.set_ylim(0, 2.2)
    nopeus.spines["right"].set_visible(True)
    vasen.set(xlabel="x", ylabel="pitoisuus", ylim=(0, 1.1))
    vasen.legend(frameon=False, fontsize=7.5, loc="upper right")
    t = np.arange(len(maarat)) * m.DT
    alku = maarat[0][0]
    oikea.plot(t, [s / alku for s, _ in maarat], color=KOROSTUS,
               linewidth=1.3, label="säilyvä")
    oikea.plot(t, [s / alku for _, s in maarat], color=SININEN,
               linewidth=1.3, linestyle="--", label="auki kerrottu")
    oikea.set(xlabel="aika", ylabel="aineen määrä / alkumäärä")
    oikea.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def savuvana(polku: Path) -> None:
    m = lataa("03-kuljetus/main.py")
    hila, c, _ = m.savuvana(160)
    x, y = hila.keskipisteet()
    fig = uusi(5.6, 2.6)
    ax = fig.add_subplot()
    taso = float(np.percentile(c, 99.5))
    kuva = ax.pcolormesh(x, y, c.T, cmap=SAVU, vmin=0.0, vmax=taso,
                         shading="nearest", rasterized=True)
    xs = np.linspace(m.LAHDE_X + 0.01, 2.0, 100)
    sigma = np.array([m.teoria(float(s)) for s in xs])
    for merkki in (1.0, -1.0):
        ax.plot(xs, 0.5 + merkki * 2.0 * sigma, color="black",
                linewidth=0.8, linestyle="--")
    ax.plot([], [], color="black", linewidth=0.8, linestyle="--",
            label="teoria: ±2 keskihajontaa")
    ax.set(xlabel="x (m)", ylabel="y (m)", aspect="equal")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.colorbar(kuva, ax=ax, shrink=0.8, label="pitoisuus")
    tallenna(fig, polku)


# --- Luku 4 -------------------------------------------------------------

def advektio(polku: Path) -> None:
    m = lataa("04-advektio.py")
    n = 100
    alku = m.porras_ja_kumpu(n)
    x = (np.arange(n) + 0.5) / n
    fig = uusi(5.6, 3.8, 160)
    akselit = fig.subplots(2, 2, sharex=True, sharey=True)
    otsikot = ("keskeis (40 askelta)", "vastavirta", "Lax–Wendroff",
               "rajoitettu (van Leer)")
    for ax, (_, vuo), otsikko in zip(akselit.ravel(), m.KAAVIOT, otsikot,
                                     strict=True):
        if otsikko.startswith("keskeis"):
            c = alku.copy()
            for _ in range(40):
                c = m.askel(c, 0.5, vuo)
            tarkka = np.roll(alku, 20)
        else:
            c = m.kierros(alku, 0.5, vuo)
            tarkka = alku
        ax.plot(x, tarkka, color=VAALEA, linewidth=1.5)
        ax.plot(x, c, color=KOROSTUS, linewidth=1.0)
        ax.set_title(otsikko, fontsize=8.5)
        ax.set_ylim(-0.4, 1.4)
    for ax in akselit[1]:
        ax.set_xlabel("x")
    for ax in akselit[:, 0]:
        ax.set_ylabel("c")
    tallenna(fig, polku)


def numdiff(polku: Path) -> None:
    m = lataa("04-numdiff.py")
    x = (np.arange(m.N) + 0.5) * m.H
    courant = 0.5
    fig = uusi()
    ax = fig.add_subplot()
    c = np.exp(-0.5 * ((x - 0.25) / m.LEVEYS) ** 2)
    ax.plot(x, c, color=VAALEA, linewidth=1.2, label="alku")
    askelia = round(0.5 / (courant * m.H))
    for _ in range(askelia):
        c = c - courant * (c - np.roll(c, 1))
    ax.plot(x, c, color=KOROSTUS, linewidth=1.3,
            label="vastavirta, matka 0,5")
    d = m.NOPEUS * m.H * (1.0 - courant) / 2.0
    s2 = m.LEVEYS**2 + 2.0 * d * 0.5
    ennuste = m.LEVEYS / math.sqrt(s2) * np.exp(-0.5 * (x - 0.75) ** 2 / s2)
    ax.plot(x, ennuste, color="black", linewidth=0.8, linestyle="--",
            label="diffuusioyhtälö, D = u h (1 − C) / 2")
    ax.plot(x, np.exp(-0.5 * ((x - 0.75) / m.LEVEYS) ** 2), color=HARMAA,
            linewidth=0.8, linestyle=":", label="tarkka advektio")
    ax.set(xlabel="x", ylabel="c", ylim=(0, 1.45))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncols=2)
    tallenna(fig, polku)


# --- Luku 5 -------------------------------------------------------------

def peclet(polku: Path) -> None:
    m = lataa("05-peclet.py")
    fig = uusi(5.6, 2.5)
    akselit = fig.subplots(1, 2, sharey=True)
    tihea = np.linspace(0.0, 1.0, 600)
    for ax, n in zip(akselit, (20, 80), strict=True):
        ax.plot(tihea, m.tarkka(tihea), color=VAALEA, linewidth=1.8,
                label="tarkka")
        x, c = m.ratkaise(n, "keskeis")
        ax.plot(x, c, "o-", color=KOROSTUS, markersize=2.5, linewidth=0.8,
                label="keskeis")
        x, c = m.ratkaise(n, "vastavirta")
        ax.plot(x, c, "s-", color=SININEN, markersize=2.5, linewidth=0.8,
                label="vastavirta")
        ax.set_title(f"{n} väliä, hilan Pe = {m.PECLET / n:g}".replace(
            ".", ","), fontsize=8.5)
        ax.set(xlabel="x", xlim=(0.6, 1.0))
    akselit[0].set_ylabel("c")
    akselit[0].legend(frameon=False, fontsize=7.5, loc="upper left")
    tallenna(fig, polku)


def vino(polku: Path) -> None:
    m = lataa("05-vino.py")
    fig = uusi(6.2, 2.4)
    akselit = fig.subplots(1, 3)
    layout = fig.get_layout_engine()
    assert layout is not None
    layout.set(wspace=0.08)
    for ax, kulma in zip(akselit[:2], (0.0, 45.0), strict=True):
        hila, c = m.vana(80, kulma, "vastavirta")
        x, y = hila.keskipisteet()
        ax.pcolormesh(x, y, c.T, cmap=SAVU, vmin=0.0,
                      vmax=float(np.percentile(c, 99.3)), shading="nearest",
                      rasterized=True)
        ax.set(aspect="equal", xticks=(0, 0.5, 1), yticks=(0, 0.5, 1))
        ax.set_title(f"tuuli {kulma:g}°", fontsize=8.5)
    # Poikkileikkaus mittauskohdassa: sama kaista kuin esimerkin funktiossa.
    ax = akselit[2]
    for kulma, vari in ((0.0, HARMAA), (45.0, KOROSTUS)):
        hila, c = m.vana(80, kulma, "vastavirta")
        a = math.radians(kulma)
        x, y = hila.keskipisteet()
        x0 = (round(m.LAHDE * hila.nx) + 0.5) * hila.h
        dx, dy = x[:, None] - x0, y[None, :] - x0
        pitkin = dx * math.cos(a) + dy * math.sin(a)
        poikki = -dx * math.sin(a) + dy * math.cos(a)
        kaista = np.abs(pitkin - m.MATKA) < hila.h / 2
        jarj = np.argsort(poikki[kaista])
        arvot = c[kaista][jarj]
        ax.plot(poikki[kaista][jarj], arvot / np.max(arvot), color=vari,
                linewidth=1.2, label=f"{kulma:g}°")
    s = np.linspace(-0.3, 0.3, 200)
    oikea = math.sqrt(2.0 * m.DIFFUUSIO * m.MATKA / m.TUULI)
    ax.plot(s, np.exp(-0.5 * (s / oikea) ** 2), color="black", linewidth=0.8,
            linestyle="--", label="fysiikka")
    ax.set(xlabel="etäisyys vanan akselista", xlim=(-0.3, 0.3),
           ylim=(0, 1.3), xticks=(-0.2, 0.0, 0.2), box_aspect=1.0,
           yticks=(0, 0.5, 1))
    ax.set_title("poikkileikkaus", fontsize=8.5)
    ax.legend(frameon=False, fontsize=7, loc="upper center", ncols=3,
              handlelength=1.0, columnspacing=0.8, handletextpad=0.4)
    tallenna(fig, polku)


# --- Luku 6 -------------------------------------------------------------

def hila(polku: Path) -> None:
    """Periaatekuva: porrastetun hilan muuttujien paikat."""
    fig = uusi(4.6, 2.6)
    ax = fig.add_subplot()
    n = 3
    for i in range(n):
        for j in range(n):
            ax.add_patch(Rectangle((i, j), 1, 1, fill=False,
                                   edgecolor=VAALEA, linewidth=0.8))
            ax.plot(i + 0.5, j + 0.5, "o", color=KOROSTUS, markersize=4.5)
    for i in range(n + 1):
        for j in range(n):
            ax.annotate("", (i + 0.16, j + 0.5), (i - 0.16, j + 0.5),
                        arrowprops={"arrowstyle": "->", "color": SININEN,
                                    "linewidth": 1.2})
    for i in range(n):
        for j in range(n + 1):
            ax.annotate("", (i + 0.5, j + 0.16), (i + 0.5, j - 0.16),
                        arrowprops={"arrowstyle": "->", "color": HARMAA,
                                    "linewidth": 1.2})
    ax.add_patch(Rectangle((1, 1), 1, 1, fill=False, edgecolor=KOROSTUS,
                           linewidth=1.6))
    ax.plot(3.9, 2.5, "o", color=KOROSTUS, markersize=4.5)
    ax.text(4.1, 2.5, "paine p[i, j]: ruudun keskellä", va="center",
            fontsize=8)
    ax.annotate("", (4.06, 1.9), (3.74, 1.9),
                arrowprops={"arrowstyle": "->", "color": SININEN,
                            "linewidth": 1.2})
    ax.text(4.1, 1.9, "u[i, j]: ruudun vasemmalla pinnalla", va="center",
            fontsize=8)
    ax.annotate("", (3.9, 1.46), (3.9, 1.14),
                arrowprops={"arrowstyle": "->", "color": HARMAA,
                            "linewidth": 1.2})
    ax.text(4.1, 1.3, "v[i, j]: ruudun alapinnalla", va="center", fontsize=8)
    ax.text(4.1, 0.55, "Ruudun massatase käyttää\nsen neljää pintanopeutta.",
            va="center", fontsize=8, color=KOROSTUS)
    ax.set(xlim=(-0.3, 7.6), ylim=(-0.3, 3.3), aspect="equal")
    ax.axis("off")
    tallenna(fig, polku)


def projektio(polku: Path) -> None:
    m = lataa("06-projektio.py")
    fig = uusi(5.6, 2.4, 160)
    akselit = fig.subplots(1, 3)
    kesket = m.kesket
    harva = slice(1, None, 3)
    kentat = ((m.u, m.v, "ennen: pyörre + lähteet"),
              (m.gx, m.gy, "poistettu gradientti"),
              (m.u2, m.v2, "jälkeen: lähteetön"))
    for ax, (u, v, otsikko) in zip(akselit, kentat, strict=True):
        div = m.divergenssi(u, v)
        ax.pcolormesh(kesket, kesket, div.T, cmap=KARTTA, vmin=-10, vmax=10,
                      shading="nearest", rasterized=True)
        uc = 0.5 * (u[:-1, :] + u[1:, :])
        vc = 0.5 * (v[:, :-1] + v[:, 1:])
        ax.quiver(kesket[harva], kesket[harva], uc[harva, harva].T,
                  vc[harva, harva].T, scale=28, width=0.006, color="black")
        ax.set(aspect="equal", xticks=[], yticks=[])
        ax.set_title(otsikko, fontsize=8)
    tallenna(fig, polku)


# --- Luku 7 -------------------------------------------------------------

def taylor_green(polku: Path) -> None:
    from virta import Ratkaisija, Tila, liike_energia, pyorteisyys
    m = lataa("07-virta/main.py")
    fig = uusi(5.6, 2.5, 150)
    vasen, keski, oikea = fig.subplots(1, 3, width_ratios=(1, 1, 1))
    teht = m.tehtava(32)
    u, v = m.tarkka(teht, 0.0)
    kulmat = np.linspace(0.0, math.pi, teht.nx + 1)[1:-1]
    vasen.pcolormesh(kulmat, kulmat, pyorteisyys(teht, u, v).T, cmap=KARTTA,
                     shading="gouraud", rasterized=True)
    tila = Tila(u, v, np.zeros((32, 32)))
    virtaviivat(vasen, teht, tila, 9, "black")
    vasen.set(aspect="equal", xticks=[], yticks=[])
    vasen.set_title("pyörre ja virtaviivat", fontsize=8.5)
    # Energian vaimeneminen.
    ratkaisija = Ratkaisija(teht)
    alku = liike_energia(teht, u, v)
    ajat, energiat = [0.0], [1.0]
    for _ in range(1000):
        tila = ratkaisija.askel(tila, 0.005)
        ajat.append(tila.t)
        energiat.append(liike_energia(teht, tila.u, tila.v) / alku)
    t = np.array(ajat)
    keski.plot(t, np.exp(-4.0 * m.NU * t), color=VAALEA, linewidth=2,
               label="tarkka")
    keski.plot(t[::80], np.array(energiat)[::80], "o", color=KOROSTUS,
               markersize=3, label="laskettu")
    keski.set(xlabel="aika", ylabel="liike-energia / alku")
    keski.legend(frameon=False, fontsize=7.5)
    # Paikan kertaluku.
    ruudut = np.array([8, 16, 32, 64])
    virheet = np.array([m.virhe(int(n), 800, "AB2") for n in ruudut])
    oikea.loglog(ruudut, virheet, "o-", color=KOROSTUS, markersize=3.5,
                 linewidth=1, label="suurin virhe")
    oikea.loglog(ruudut, virheet[0] * (ruudut[0] / ruudut) ** 2.0,
                 color=HARMAA, linewidth=0.8, linestyle="--",
                 label="kulmakerroin −2")
    oikea.set(xlabel="ruutuja / sivu")
    oikea.set_xticks(ruudut, [str(n) for n in ruudut])
    oikea.minorticks_off()
    oikea.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def aika(polku: Path) -> None:
    from virta import Ratkaisija, Reuna, Tehtava, Tila, liike_energia
    m = lataa("07-aika.py")
    liukuva = Reuna("liukuva")
    teht = Tehtava(m.N, m.N, math.pi, math.pi, m.NU, liukuva, liukuva,
                   liukuva, liukuva)
    fig = uusi()
    ax = fig.add_subplot()
    for kaavio, dt, vari, tyyli in (("Euler", 0.02, SININEN, "-"),
                                    ("Euler", 0.01, HARMAA, "-"),
                                    ("AB2", 0.02, KOROSTUS, "--")):
        ratkaisija = Ratkaisija(teht)
        u, v = m.alkutila(teht)
        alku = liike_energia(teht, u, v)
        tila = Tila(u, v, np.zeros((m.N, m.N)))
        ajat, energiat = [0.0], [1.0]
        with np.errstate(all="ignore"):
            for _ in range(round(m.LOPPU / dt)):
                tila = ratkaisija.askel(tila, dt, kaavio)
                e = liike_energia(teht, tila.u, tila.v) / alku
                if not math.isfinite(e) or e > 1.2:
                    break
                ajat.append(tila.t)
                energiat.append(e)
        ax.plot(ajat, energiat, color=vari, linewidth=1.3, linestyle=tyyli,
                label=f"{kaavio}, dt = {dt:g}".replace(".", ","))
    ax.set(xlabel="aika", ylabel="liike-energia / alku", ylim=(0.97, 1.05))
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    tallenna(fig, polku)


# --- Luku 8 -------------------------------------------------------------

def kanava(polku: Path) -> None:
    m = lataa("08-kanava.py")
    fig = uusi(5.6, 4.2, 140)
    yla, ala = fig.subfigures(2, 1, height_ratios=(1, 1.5))
    ax = yla.subplots()
    teht, tila, _ = m.kanava(40.0, 6.0)
    x = np.linspace(0.0, teht.lx, teht.nx + 1)
    y = (np.arange(teht.ny) + 0.5) * teht.dy
    kuva = ax.pcolormesh(x, y, tila.u.T, cmap=KARTTA, shading="gouraud",
                         rasterized=True, vmin=0, vmax=1.5)
    virtaviivat(ax, teht, tila, 9, "white")
    ax.set(xlabel="x", ylabel="y", xlim=(0, 4))
    ax.set_title("vaakanopeus ja virtaviivat, Re = 40", fontsize=8.5)
    yla.colorbar(kuva, ax=ax, shrink=0.9)
    vasen, oikea = ala.subplots(1, 2)
    for kohta, vari in ((0.25, VAALEA), (0.5, HARMAA), (1.0, SININEN),
                        (5.0, KOROSTUS)):
        vasen.plot(tila.u[round(kohta / teht.dx), :], y, color=vari,
                   linewidth=1.2, label=f"x = {kohta:g}".replace(".", ","))
    vasen.plot(6.0 * y * (1.0 - y), y, color="black", linewidth=0.7,
               linestyle="--", label="paraabeli")
    vasen.set(xlabel="vaakanopeus", ylabel="y")
    vasen.legend(frameon=False, fontsize=7)
    for reynolds, pituus, vari in ((20.0, 6.0, VAALEA), (40.0, 6.0, HARMAA),
                                   (80.0, 10.0, KOROSTUS)):
        teht, tila, _ = m.kanava(reynolds, pituus)
        xs = np.linspace(0.0, teht.lx, teht.nx + 1)
        oikea.plot(xs, m.keskilinja(tila), color=vari, linewidth=1.2,
                   label=f"Re = {reynolds:g}")
    oikea.set(xlabel="x", ylabel="keskilinjan nopeus", xlim=(0, 6))
    oikea.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def _este_tehtava(m: Any, etumatka: float, jalkimatka: float) -> Any:
    """Sama tehtävä kuin esimerkin 08-reunat funktiossa, tila talteen."""
    from virta import Ratkaisija, Reuna, Tehtava, tasapainoon, vakaa_askel
    nx = round((etumatka + m.SIVU + jalkimatka) / m.H)
    i0, k = round(etumatka / m.H), round(m.SIVU / m.H)
    este = np.zeros((nx, m.NY), dtype=np.bool_)
    este[i0:i0 + k, m.NY // 2 - k // 2:m.NY // 2 + k // 2] = True
    teht = Tehtava(nx, m.NY, nx * m.H, 1.0, m.SIVU / m.REYNOLDS,
                   vasen=Reuna("sisään", np.ones(m.NY)), oikea=Reuna("ulos"),
                   este=este)
    ratkaisija = Ratkaisija(teht)
    tila, _ = tasapainoon(ratkaisija, ratkaisija.lepotila(),
                          vakaa_askel(teht, 2.5))
    return teht, tila, ratkaisija


def reunat(polku: Path) -> None:
    m = lataa("08-reunat.py")
    fig = uusi(5.6, 3.6, 140)
    akselit = fig.subplots(2, 1)
    for ax, jalki, otsikko in (
            (akselit[0], 3.0, "ulosvirtausreuna kaukana"),
            (akselit[1], 0.375, "ulosvirtausreuna 0,375 esteen takana")):
        teht, tila, ratkaisija = _este_tehtava(m, 3.0, jalki)
        u = tila.u.copy()
        u[~ratkaisija.auki_u & (np.arange(teht.nx + 1)[:, None] > 0)
          & (np.arange(teht.nx + 1)[:, None] < teht.nx)] = 0.0
        x = np.linspace(0.0, teht.lx, teht.nx + 1)
        y = (np.arange(teht.ny) + 0.5) * teht.dy
        kuva = ax.pcolormesh(x, y, u.T, cmap=KARTTA, shading="gouraud",
                             rasterized=True, vmin=-0.2, vmax=1.9)
        from virta import Tila
        virtaviivat(ax, teht, Tila(u, tila.v, tila.p), 14, "white")
        ax.add_patch(Rectangle((3.0, 0.5 - m.SIVU / 2), m.SIVU, m.SIVU,
                               facecolor="black"))
        ax.set(xlim=(2.4, 4.3), ylim=(0.15, 0.85), aspect="equal",
               ylabel="y")
        ax.set_title(otsikko, fontsize=8.5)
        ax.axvline(teht.lx, color="black", linewidth=1.0, linestyle=":")
    akselit[1].set_xlabel("x")
    fig.colorbar(kuva, ax=akselit, shrink=0.7, label="vaakanopeus")
    tallenna(fig, polku)


# --- Luku 9 -------------------------------------------------------------

def onkalo(polku: Path) -> None:
    from virta import virtafunktio
    m = lataa("09-onkalo.py")
    fig = uusi(5.6, 2.9, 150)
    akselit = fig.subplots(1, 2)
    for ax, (reynolds, n, kaavio) in zip(
            akselit, ((100.0, 64, "Euler"), (400.0, 48, "AB2")), strict=True):
        teht, tila, _ = m.onkalo(reynolds, n, kaavio)
        psi = virtafunktio(teht, tila.u)
        k = np.linspace(0.0, 1.0, n + 1)
        tasot = np.concatenate((np.linspace(float(psi.min()), -1e-4, 12),
                                [1e-5, 1e-4, 5e-4]))
        ax.contour(k, k, psi.T, levels=tasot, colors=HARMAA, linewidths=0.7,
                   linestyles="solid")
        i, j = np.unravel_index(int(np.argmin(psi)), psi.shape)
        ax.plot(i / n, j / n, "+", color=KOROSTUS, markersize=8)
        ax.annotate("", (0.75, 1.04), (0.25, 1.04), annotation_clip=False,
                    arrowprops={"arrowstyle": "->", "color": KOROSTUS})
        ax.set(aspect="equal", xticks=(0, 0.5, 1), yticks=(0, 0.5, 1))
        ax.set_title(f"Re = {reynolds:g}", fontsize=8.5, pad=12)
        for sivu in ("top", "right"):
            ax.spines[sivu].set_visible(True)
    tallenna(fig, polku)


def onkalo_hilat(polku: Path) -> None:
    m = lataa("09-onkalo.py")
    fig = uusi(5.6, 2.6)
    vasen, oikea = fig.subplots(1, 2)
    arvot = []
    for n, vari in ((16, VAALEA), (32, HARMAA), (64, KOROSTUS)):
        teht, tila, _ = m.onkalo(100.0, n)
        y = (np.arange(n) + 0.5) / n
        vasen.plot(tila.u[n // 2, :], y, color=vari, linewidth=1.2,
                   label=f"{n} × {n}")
        arvot.append(m.tunnusluvut(teht, tila).u_min)
    vasen.set(xlabel="u pystysuoralla keskilinjalla", ylabel="y")
    vasen.legend(frameon=False, fontsize=7.5)
    p, raja, _ = m.richardson(*arvot)
    h = np.array([1 / 16, 1 / 32, 1 / 64])
    tihea = np.linspace(0.0, 1 / 16, 50)
    c = (arvot[2] - raja) / h[2] ** p
    oikea.plot(tihea, raja + c * tihea**p, color=VAALEA, linewidth=1,
               linestyle="--",
               label=f"raja + C·h^{p:.2f}".replace(".", ","))
    oikea.plot(h, arvot, "o", color=KOROSTUS, markersize=4, label="lasketut")
    oikea.plot([0], [raja], "*", color="black", markersize=8,
               label="ekstrapoloitu")
    oikea.set(xlabel="ruudun sivu h", ylabel="keskilinjan pienin u")
    oikea.legend(frameon=False, fontsize=7.5, loc="lower right")
    tallenna(fig, polku)


# --- Luku 10 ------------------------------------------------------------

def este(polku: Path) -> None:
    from virta import pyorteisyys
    m = lataa("10-este.py")
    fig = uusi(5.6, 6.4, 120)
    yla, toinen, keski, ala = fig.subplots(4, 1, height_ratios=(1, 1, 1, 0.8))
    ajot = {}
    for ax, vastavirta, otsikko in (
            (yla, 0.0, "pyörteisyys, keskeisdifferenssi"),
            (toinen, 0.3, "pyörteisyys, sekoitus 0,3"),
            (keski, 1.0, "pyörteisyys, vastavirta")):
        ajo = m.aja(30, vastavirta)
        ajot[vastavirta] = ajo
        teht = ajo.teht
        w = pyorteisyys(teht, ajo.tila.u, ajo.tila.v)
        x = np.linspace(0.0, teht.lx, teht.nx + 1)[1:-1]
        y = np.linspace(0.0, teht.ly, teht.ny + 1)[1:-1]
        ax.pcolormesh(x, y, w.T, cmap=KARTTA, vmin=-12, vmax=12,
                      shading="gouraud", rasterized=True)
        k = round(m.SIVU * teht.ny)
        i0 = round(m.ESTE_X * teht.ny) - k // 2
        j0 = teht.ny // 2 - k // 2 + 1
        ax.add_patch(Rectangle((i0 / teht.ny, j0 / teht.ny), m.SIVU, m.SIVU,
                               facecolor="black"))
        ax.set(aspect="equal", xlim=(0, m.PITUUS), ylim=(0, 1),
               yticks=(0, 1))
        ax.set_title(otsikko, fontsize=8.5)
    for vastavirta, vari in ((0.0, KOROSTUS), (0.3, HARMAA), (1.0, SININEN)):
        ajo = ajot[vastavirta]
        ala.plot(ajo.ajat, ajo.v_mitta, color=vari, linewidth=0.9)
    ala.set(xlabel="aika", xlim=(0, m.LOPPU))
    ala.set_title("pystynopeus mittapisteessä: keskeis (ruskea), sekoitus "
                  "(harmaa), vastavirta (sininen)", fontsize=8.5)
    tallenna(fig, polku)


# --- Luku 11 ------------------------------------------------------------

def hinta(polku: Path) -> None:
    m = lataa("11-mittakaavat.py")
    fig = uusi()
    ax = fig.add_subplot()
    re = np.logspace(3, 8, 50)
    aika_s = np.array([m.suora_simulointi(float(r))[2] for r in re]) / m.NOPEUS
    ax.loglog(re, aika_s, color=KOROSTUS, linewidth=1.5)
    for raja, nimi in ((3600.0, "tunti"), (86400.0 * 30, "kuukausi"),
                       (3.156e7 * 100, "sata vuotta")):
        ax.axhline(raja, color=VAALEA, linewidth=0.8)
        ax.text(1.2e3, raja * 1.6, nimi, fontsize=7.5, color=HARMAA)
    for r, nimi in ((1.2e4, "vesi hanasta"), (8.4e6, "henkilöauto")):
        ax.axvline(r, color=HARMAA, linewidth=0.8, linestyle=":")
        ax.text(r * 1.25, 3.0, nimi, fontsize=7.5, color=HARMAA, rotation=90,
                va="bottom")
    ax.set(xlabel="Reynoldsin luku", ylabel="laskenta-aika (s)",
           ylim=(1, 1e16))
    tallenna(fig, polku)


def seinalaki(polku: Path) -> None:
    """Periaatekuva: nopeusprofiili seinän lähellä seinäyksiköissä."""
    fig = uusi()
    ax = fig.add_subplot()
    yp = np.logspace(-0.3, 3, 300)
    ax.semilogx(yp[yp < 12], yp[yp < 12], color=SININEN, linewidth=1.3,
                label="viskoosi alikerros: u⁺ = y⁺")
    ax.semilogx(yp[yp > 8], np.log(yp[yp > 8]) / 0.41 + 5.0, color=KOROSTUS,
                linewidth=1.3, label="logaritminen laki")
    ax.axvspan(0.5, 2, color=SININEN, alpha=0.12, linewidth=0)
    ax.axvspan(30, 300, color=KOROSTUS, alpha=0.12, linewidth=0)
    ax.text(1.0, 22.5, "ruutu tähän:\nlasketaan\nseinään asti", ha="center",
            fontsize=7.5, color=SININEN)
    ax.text(95, 3.0, "ruutu tähän:\nseinäfunktio", ha="center", fontsize=7.5,
            color=KOROSTUS)
    ax.set(xlabel="etäisyys seinästä y⁺", ylabel="nopeus u⁺", ylim=(0, 27),
           xlim=(0.5, 1000))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left",
              bbox_to_anchor=(0.16, 1.0))
    tallenna(fig, polku)


# --- Luku 12 ------------------------------------------------------------

def suppeneminen(polku: Path) -> None:
    m = lataa("12-suppeneminen.py")
    fig = uusi()
    ax = fig.add_subplot()
    askeleet = np.array([h[0] for h in m.historia])
    jaannos = np.array([h[1] for h in m.historia])
    psi = np.array([h[2] for h in m.historia])
    ero = np.abs(psi / m.lopullinen - 1.0)
    ax.semilogy(askeleet, jaannos, "o-", color=HARMAA, markersize=3,
                linewidth=1, label="jäännös")
    ax.semilogy(askeleet[:-1], ero[:-1], "s-", color=KOROSTUS, markersize=3,
                linewidth=1, label="pyörteen voimakkuuden suhteellinen ero")
    ax.set(xlabel="aika-askel")
    ax.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def monihila(polku: Path) -> None:
    m = lataa("12-monihila.py")
    n = 63
    h = 1.0 / (n + 1)
    x = np.linspace(0.0, 1.0, n + 2)
    f = np.zeros((n + 2, n + 2))
    f[1:-1, 1:-1] = (np.exp(x[1:-1, None]) * np.sin(3.0 * x[None, 1:-1])
                     + np.where(x[1:-1, None] > 0.5, 5.0, 0.0))
    fig = uusi(5.6, 2.6)
    vasen, oikea = fig.subplots(1, 2)
    # Vasen: Jacobi poistaa virheen nopean osan, hidas jää.
    rng = np.random.default_rng(1)
    virhe = np.zeros((n + 2, n + 2))
    virhe[1:-1, 1:-1] = (np.sin(math.pi * x[1:-1, None])
                         * np.sin(math.pi * x[None, 1:-1])
                         + 0.4 * rng.standard_normal((n, n)))
    nolla = np.zeros_like(f)
    for kierros, vari in ((0, VAALEA), (5, HARMAA), (50, KOROSTUS)):
        e = virhe.copy()
        for _ in range(kierros):
            e = m.jacobi(e, nolla, h)
        vasen.plot(x, e[:, n // 2], color=vari, linewidth=1.0,
                   label=f"{kierros} kierrosta")
    vasen.set(xlabel="x", ylabel="virhe keskirivillä")
    vasen.legend(frameon=False, fontsize=7.5)
    # Oikea: jäännös kierrosten funktiona.
    def normi(u: Any) -> float:
        return float(np.sqrt(np.sum(m.jaannos(u, f, h) ** 2)))
    for nimi, vari, kierroksia in (("Jacobi", HARMAA, 400),
                                   ("monihila", KOROSTUS, 12)):
        u = np.zeros_like(f)
        alku = normi(u)
        arvot = [1.0]
        for _ in range(kierroksia):
            u = m.jacobi(u, f, h, 1.0) if nimi == "Jacobi" else m.v_kierros(
                u, f, h)
            arvot.append(normi(u) / alku)
        oikea.semilogy(arvot, color=vari, linewidth=1.2, label=nimi)
    oikea.set(xlabel="kierros", ylabel="jäännös / alku", xlim=(0, 100),
              ylim=(1e-9, 2))
    oikea.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    valitut = set(sys.argv[2:])
    for nimi, piirra in (
            ("levy", levy), ("voitelukalvo", voitelukalvo),
            ("tilavuus", tilavuus), ("sailyvyys", sailyvyys),
            ("savuvana", savuvana), ("advektio", advektio),
            ("numdiff", numdiff), ("peclet", peclet), ("vino", vino),
            ("hila", hila), ("projektio", projektio),
            ("taylor-green", taylor_green), ("aika", aika),
            ("kanava", kanava), ("reunat", reunat), ("onkalo", onkalo),
            ("onkalo-hilat", onkalo_hilat), ("este", este),
            ("hinta", hinta), ("seinalaki", seinalaki),
            ("suppeneminen", suppeneminen), ("monihila", monihila)):
        if not valitut or nimi in valitut:
            piirra(kohde / f"{nimi}.png")


if __name__ == "__main__":
    main()
