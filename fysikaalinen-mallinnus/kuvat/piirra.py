"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

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
from matplotlib.tri import Triangulation

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT / "07-pienfem"))

KOROSTUS = "#9A6524"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
SININEN = "#2F6B8A"
KARTTA = LinearSegmentedColormap.from_list(
    "lampo", ["#243B53", "#5B8FA8", "#F3EBDD", "#D08A3C", "#7A2E12"])
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
    nimi = "esimerkki_" + tiedosto.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(nimi, ESIMERKIT / tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    sys.modules[nimi] = moduuli
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(moduuli)
    return moduuli


def kolmiointi(verkko: Any) -> Triangulation:
    return Triangulation(verkko.pisteet[:, 0], verkko.pisteet[:, 1],
                         verkko.kolmiot)


# --- Luku 1 -------------------------------------------------------------

def ripa(polku: Path) -> None:
    m = lataa("01-ripa.py")
    fig = uusi()
    ax = fig.add_subplot()
    tihea = np.linspace(0.0, m.PITUUS, 200)
    ax.plot(1e3 * tihea, m.tarkka(tihea), color=HARMAA, linewidth=1.2,
            label="tarkka ratkaisu")
    for n, vari, merkki in ((3, VAALEA, "s"), (7, KOROSTUS, "o")):
        x, u = m.ratkaise(n)
        ax.plot(1e3 * x, u, merkki + "-", color=vari, markersize=3.5,
                linewidth=0.8, label=f"{n} sisäpistettä")
    ax.set(xlabel="paikka tangossa (mm)", ylabel="lämpötila (°C)")
    ax.legend(frameon=False, fontsize=8, loc="upper center")
    tallenna(fig, polku)


# --- Luku 2 -------------------------------------------------------------

def tase(polku: Path) -> None:
    m = lataa("02-tase.py")
    fig = uusi(5.6, 2.6)
    ax1, ax2 = fig.subplots(1, 2)
    x = 1e3 * (np.arange(m.N) + 0.5) * m.DX
    a = np.zeros(m.N)
    b = np.zeros(m.N)
    ajat, ea, eb = [0.0], [0.0], [0.0]
    for kierros in range(1, 30001):
        a, b = m.askel_sailyva(a), m.askel_sailymaton(b)
        if kierros % 500 == 0:
            ajat.append(kierros * m.DT)
            ea.append(m.energia(a))
            eb.append(m.energia(b))
        if kierros in (3000, 12000, 30000):
            ax1.plot(x, a, color=KOROSTUS, linewidth=1)
            ax1.text(x[3], a[3] + 0.6, f"{kierros * m.DT:.0f} s",
                     fontsize=7, color=KOROSTUS)
    ax1.axvline(100.0, color=VAALEA, linewidth=0.8, linestyle="--")
    ax1.text(50, 0.4, "kupari", ha="center", fontsize=7, color=HARMAA)
    ax1.text(150, 0.4, "teräs", ha="center", fontsize=7, color=HARMAA)
    ax1.set(xlabel="paikka (mm)", ylabel="lämpötilan nousu (K)")
    t = np.array(ajat)
    ax2.plot(t, m.TEHO * t, color="black", linewidth=2.2, alpha=0.25,
             label="syötetty energia")
    ax2.plot(t, ea, color=KOROSTUS, linewidth=1, label="säilyvä muoto")
    ax2.plot(t, eb, color=HARMAA, linewidth=1, linestyle="--",
             label="auki kerrottu muoto")
    ax2.set(xlabel="aika (s)", ylabel="energia tangossa (J)",
            ylim=(0, 3000))
    ax2.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


def dimensioton(polku: Path) -> None:
    m = lataa("02-dimensioton.py")
    fig = uusi(4.2, 2.6)
    ax = fig.add_subplot()
    fo = np.linspace(0.005, 2.2, 300)
    ax.plot(fo, [m.keskikohta(f) for f in fo], color=KOROSTUS, linewidth=1.3)
    for theta in (0.5, 0.01):
        f = m.fo_kun(theta)
        ax.plot([f], [theta], "o", color=HARMAA, markersize=4)
        ax.annotate(f"Fo = {f:.2f}".replace(".", ","), (f, theta),
                    textcoords="offset points", xytext=(6, 6), fontsize=8,
                    color=HARMAA)
    ax.set(xlabel="Fourier'n luku Fo = αt / L²",
           ylabel="keskikohdan θ", ylim=(0, 1.05))
    tallenna(fig, polku)


# --- Luku 3 -------------------------------------------------------------

def levy(polku: Path) -> None:
    m = lataa("03-levy.py")
    fig = uusi(3.9, 3.0, dpi=180)
    ax = fig.add_subplot()
    n = 127
    u = np.zeros((n + 2, n + 2))
    u[1:-1, 1:-1] = m.ratkaise(n)
    u[0, :] = m.T_KUUMA
    x = np.linspace(0.0, 1.0, n + 2)
    kuva = ax.pcolormesh(x, x, u, cmap=KARTTA, shading="gouraud",
                         rasterized=True)
    ax.contour(x, x, u, levels=[10, 25, 50, 75], colors="white",
               linewidths=0.6)
    ax.plot([0.5], [0.5], "+", color="black", markersize=6)
    ax.text(0.52, 0.52, "25 °C", fontsize=7)
    ax.set(aspect="equal", xlabel="x", ylabel="y")
    fig.colorbar(kuva, ax=ax, label="°C", shrink=0.85)
    tallenna(fig, polku)


# --- Luku 4 -------------------------------------------------------------

def ftcs(polku: Path) -> None:
    m = lataa("04-ftcs.py")
    fig = uusi(5.6, 2.4)
    akselit = fig.subplots(1, 2, sharey=False)
    x = np.linspace(0.0, 1.0, m.N + 1)
    for ax, r, askeleet in ((akselit[0], 0.50, (0, 100, 300, 500)),
                            (akselit[1], 0.51, (0, 300, 400, 440))):
        u = np.sin(math.pi * x) + m.hairio
        for k in range(max(askeleet) + 1):
            if k in askeleet:
                ax.plot(x, u, linewidth=0.9,
                        color=KOROSTUS if k == max(askeleet) else HARMAA,
                        alpha=1.0 if k in (0, max(askeleet)) else 0.6)
            u = m.ftcs(u, r)
        ax.set(xlabel="x", title=f"r = {r:.2f}".replace(".", ","))
        ax.title.set_fontsize(9)
    akselit[0].set_ylabel("u")
    tallenna(fig, polku)


def porras(polku: Path) -> None:
    m = lataa("04-implisiittinen.py")
    fig = uusi(4.6, 2.5)
    ax = fig.add_subplot()
    ax.plot(m.x, m.alku, color=VAALEA, linewidth=1, label="alkutila")
    for nimi, theta, vari in (("implisiittinen Euler", 1.0, HARMAA),
                              ("Crank–Nicolson", 0.5, KOROSTUS)):
        u = m.alku.copy()
        for _ in range(2):
            u = m.theta_askel(u, m.r, theta)
        ax.plot(m.x, u, color=vari, linewidth=1.1, label=nimi)
    ax.set(xlabel="x", ylabel="u kahden askeleen jälkeen")
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


def biot(polku: Path) -> None:
    m = lataa("04-biot.py")
    fig = uusi(4.6, 2.6)
    ax = fig.add_subplot()
    x = 1e3 * (np.arange(m.N) + 0.5) * m.PUOLIKAS / m.N
    for nimi, h, t, vari in (("ilma, 600 s", 25.0, 600.0, VAALEA),
                             ("öljy, 60 s", 500.0, 60.0, HARMAA),
                             ("vesi, 10 s", 5000.0, 10.0, KOROSTUS)):
        u = m.jaahdyta(h, t, 2000)
        bi = h * m.PUOLIKAS / m.K
        ax.plot(x, u, color=vari, linewidth=1.2,
                label=f"{nimi}, Bi = {bi:.2f}".replace(".", ","))
    ax.set(xlabel="etäisyys levyn keskeltä (mm)", ylabel="lämpötila (°C)")
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    tallenna(fig, polku)


# --- Luku 5 -------------------------------------------------------------

def kieli(polku: Path) -> None:
    m = lataa("05-kieli.py")
    fig = uusi(5.6, 2.5)
    ax1, ax2 = fig.subplots(1, 2, sharey=True)
    x = np.linspace(0.0, 1.0, m.N + 1)
    vanha = m.alkuasento()
    u = m.aloitus(vanha, 1.0)
    for k in range(1, 101):
        if k in (1, 25, 50, 75, 100):
            ax1.plot(x, 1e3 * (vanha if k == 1 else u), linewidth=0.9,
                     color=KOROSTUS if k == 1 else HARMAA,
                     alpha=1.0 if k == 1 else 0.75)
        u, vanha = m.askel(u, vanha, 1.0), u
    ax1.set(xlabel="x", ylabel="poikkeama (·10⁻³)",
            title="Courantin luku 1: puoli jaksoa")
    vanha = m.alkuasento()
    u = m.aloitus(vanha, 0.5)
    for _ in range(399):
        u, vanha = m.askel(u, vanha, 0.5), u
    ax2.plot(x, 1e3 * m.alkuasento(), color=VAALEA, linewidth=1.4,
             label="tarkka")
    ax2.plot(x, 1e3 * u, color=KOROSTUS, linewidth=0.9, label="laskettu")
    ax2.set(xlabel="x", title="Courantin luku 0,5: jakson jälkeen")
    ax2.legend(frameon=False, fontsize=7)
    for ax in (ax1, ax2):
        ax.title.set_fontsize(8)
    tallenna(fig, polku)


def kalvo(polku: Path) -> None:
    m = lataa("05-kalvo.py")
    fig = uusi(5.6, 2.4)
    ax1, ax2 = fig.subplots(1, 2)
    sarja, dt = m.simuloi()
    t = np.arange(len(sarja)) * dt
    ax1.plot(t[:1300], sarja[:1300], color=KOROSTUS, linewidth=0.7)
    ax1.set(xlabel="aika", ylabel="keskipisteen poikkeama")
    pituus = 8 * len(sarja)
    spektri = np.abs(np.fft.rfft(sarja * np.hanning(len(sarja)), pituus))
    f = np.fft.rfftfreq(pituus, dt)
    ax2.semilogy(f, spektri / spektri.max(), color=HARMAA, linewidth=0.8)
    for mm, nn in ((1, 1), (1, 3), (3, 3), (1, 5), (3, 5)):
        tarkka = math.sqrt(mm * mm + nn * nn) / 2.0
        ax2.axvline(tarkka, color=KOROSTUS, linewidth=0.6, linestyle="--")
        ax2.text(tarkka, 1.6, f"({mm},{nn})", ha="center", fontsize=6,
                 color=KOROSTUS)
    ax2.set(xlabel="taajuus", ylabel="suhteellinen amplitudi",
            xlim=(0, 3.2), ylim=(1e-4, 4))
    tallenna(fig, polku)


# --- Luku 6 -------------------------------------------------------------

def hattu(polku: Path) -> None:
    m = lataa("06-kertaluku.py")
    fig = uusi(5.6, 2.4)
    ax1, ax2 = fig.subplots(1, 2)
    solmut = np.array([0.0, 0.2, 0.5, 0.7, 1.0])
    for i in range(len(solmut)):
        arvot = np.zeros(len(solmut))
        arvot[i] = 1.0
        ax1.plot(solmut, arvot, color=KOROSTUS if i == 2 else VAALEA,
                 linewidth=1.4 if i == 2 else 0.9)
    ax1.plot(solmut, 0 * solmut, "o", color=HARMAA, markersize=3)
    ax1.text(0.5, 1.03, "φ₂", ha="center", color=KOROSTUS, fontsize=9)
    ax1.set(xlabel="x", ylabel="kantafunktiot", ylim=(-0.05, 1.15))
    tihea = np.linspace(0.0, 1.0, 200)
    ax2.plot(tihea, np.sin(math.pi * tihea), color=HARMAA, linewidth=1.2,
             label="tarkka")
    tasa = np.linspace(0.0, 1.0, 5)
    ax2.plot(tasa, m.ratkaise(tasa), "o-", color=KOROSTUS, markersize=3.5,
             linewidth=1, label="4 elementtiä")
    ax2.set(xlabel="x", ylabel="u")
    ax2.legend(frameon=False, fontsize=7, loc="lower center")
    tallenna(fig, polku)


# --- Luku 7 -------------------------------------------------------------

def l_alue(polku: Path) -> None:
    import pienfem
    m = lataa("07-l-alue.py")
    fig = uusi(5.6, 2.6, dpi=180)
    ax1, ax2 = fig.subplots(1, 2)
    karkea = pienfem.l_alue(4)
    ax1.triplot(kolmiointi(karkea), color=HARMAA, linewidth=0.4)
    ax1.plot([0], [0], "o", color=KOROSTUS, markersize=4)
    ax1.set(aspect="equal", title="verkko, 8 ruutua sivulla")
    verkko = pienfem.l_alue(32)
    x, y = verkko.pisteet[:, 0], verkko.pisteet[:, 1]
    reuna = verkko.reunasolmut()
    u = pienfem.ratkaise(pienfem.jaykkyys(verkko), np.zeros(len(x)), reuna,
                         m.tarkka(x[reuna], y[reuna]))
    kuva = ax2.tripcolor(kolmiointi(verkko), u, cmap=KARTTA,
                         shading="gouraud", rasterized=True)
    ax2.tricontour(kolmiointi(verkko), u, levels=8, colors="white",
                   linewidths=0.5)
    ax2.set(aspect="equal", title="ratkaisu")
    fig.colorbar(kuva, ax=ax2, shrink=0.8)
    for ax in (ax1, ax2):
        ax.title.set_fontsize(8)
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
    tallenna(fig, polku)


def lammitin(polku: Path) -> None:
    m = lataa("07-reunaehdot.py")
    fig = uusi(4.8, 2.5, dpi=180)
    ax = fig.add_subplot()
    tri = Triangulation(1e3 * m.x, 1e3 * m.y, m.verkko.kolmiot)
    kuva = ax.tripcolor(tri, m.t, cmap=KARTTA, shading="gouraud",
                        rasterized=True)
    ax.tricontour(tri, m.t, levels=10, colors="white", linewidths=0.5)
    ax.plot([0, 0], [1e3 * m.KORKEUS / 3, 2e3 * m.KORKEUS / 3],
            color="black", linewidth=3, solid_capstyle="butt")
    ax.text(3, 25, "lämmitin", rotation=90, va="center", fontsize=7,
            color="white")
    ax.text(97, 25, "konvektio ilmaan", rotation=90, va="center",
            ha="right", fontsize=7, color="white")
    ax.set(aspect="equal", xlabel="x (mm)", ylabel="y (mm)")
    fig.colorbar(kuva, ax=ax, label="°C", shrink=0.8)
    tallenna(fig, polku)


def kertaluvut(polku: Path) -> None:
    """Luvun 7 ja 8 taulukoiden virheet samassa kuvassa."""
    import pienfem
    m7 = lataa("07-l-alue.py")
    mp = lataa("07-pienfem/main.py")
    fig = uusi(4.2, 2.8)
    ax = fig.add_subplot()
    ns = np.array([4, 8, 16, 32, 64])
    nelio, lmuoto = [], []
    for n in ns:
        v = pienfem.suorakulmio(int(n), int(n))
        r = v.reunasolmut()
        u = pienfem.ratkaise(pienfem.jaykkyys(v), pienfem.kuorma(v, mp.lahde),
                             r, np.zeros(len(r)))
        nelio.append(pienfem.l2_virhe(v, u, mp.tarkka))
        v = pienfem.l_alue(int(n))
        r = v.reunasolmut()
        x, y = v.pisteet[:, 0], v.pisteet[:, 1]
        u = pienfem.ratkaise(pienfem.jaykkyys(v), np.zeros(len(x)), r,
                             m7.tarkka(x[r], y[r]))
        lmuoto.append(pienfem.l2_virhe(v, u, m7.tarkka))
    ax.loglog(ns, nelio, "o-", color=KOROSTUS, markersize=3, linewidth=1,
              label="neliö, sileä ratkaisu")
    ax.loglog(ns, lmuoto, "s-", color=HARMAA, markersize=3, linewidth=1,
              label="L-alue, kulmasingulariteetti")
    suhde = ns / ns[0]
    ax.loglog(ns, 0.45 * nelio[0] / suhde**2, color=VAALEA, linewidth=0.8,
              linestyle="--")
    ax.loglog(ns, 2.2 * lmuoto[0] / suhde ** (4 / 3), color=VAALEA,
              linewidth=0.8, linestyle="--")
    ax.text(48, 0.45 * nelio[0] / 12.0**2 * 0.5, "h²", fontsize=8,
            color=HARMAA)
    ax.text(40, 2.2 * lmuoto[0] / 10.0 ** (4 / 3) * 1.25, "h^(4/3)",
            fontsize=8, color=HARMAA)
    ax.set_xscale("log", base=2)
    ax.set_xticks(ns, [str(int(n)) for n in ns])
    ax.minorticks_off()
    ax.set(xlabel="ruutuja yksikön matkalla (1/h)", ylabel="L2-virhe")
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    tallenna(fig, polku)


# --- Luku 9 -------------------------------------------------------------

def uloke(polku: Path) -> None:
    import pienfem
    m = lataa("09-uloke.py")
    fig = uusi(5.6, 2.2, dpi=180)
    ax = fig.add_subplot()
    from scipy.sparse.linalg import spsolve
    nx, ny = 80, 8
    verkko = pienfem.suorakulmio(nx, ny, m.PITUUS, m.KORKEUS)
    x = verkko.pisteet[:, 0]
    k = m.jaykkyys(verkko)
    f = np.zeros(2 * len(x))
    paa = np.flatnonzero(x > m.PITUUS - 1e-9)
    paino = np.full(len(paa), 1.0 / ny)
    paino[[0, -1]] *= 0.5
    f[2 * paa + 1] = -m.VOIMA * paino
    kiinni = np.flatnonzero(x < 1e-9)
    lukitut = np.concatenate([2 * kiinni, 2 * kiinni + 1])
    vapaat = np.setdiff1d(np.arange(len(f)), lukitut)
    u = np.zeros(len(f))
    u[vapaat] = spsolve(k[vapaat][:, vapaat].tocsc(), f[vapaat])
    sxx = np.empty(len(verkko.kolmiot))
    for i, solmut in enumerate(verkko.kolmiot):
        b, _ = m.venymamatriisi(verkko.pisteet[solmut])
        vapaus = np.column_stack([2 * solmut, 2 * solmut + 1]).ravel()
        sxx[i] = (m.D @ b @ u[vapaus])[0]
    kerroin = 30.0
    tri = Triangulation(verkko.pisteet[:, 0] + kerroin * u[0::2],
                        verkko.pisteet[:, 1] + kerroin * u[1::2],
                        verkko.kolmiot)
    kuva = ax.tripcolor(tri, 1e-6 * sxx, cmap=KARTTA, vmin=-60, vmax=60,
                        rasterized=True)
    ax.plot([0, 0], [-0.03, 0.13], color="black", linewidth=2)
    ax.set(aspect="equal", xlabel="x (m)", ylabel="y (m)")
    fig.colorbar(kuva, ax=ax, label="σₓₓ (MPa)", shrink=0.9,
                 orientation="horizontal", pad=0.02, aspect=40)
    tallenna(fig, polku)


def reika(polku: Path) -> None:
    import skfem as fem
    from skfem.helpers import sym_grad
    from skfem.models.elasticity import lame_parameters, linear_elasticity
    m = lataa("09-reika.py")
    fig = uusi(5.6, 2.7, dpi=180)
    ax1, ax2 = fig.subplots(1, 2)
    a = 0.2 * m.W
    karkea = m.neljannes(a, 10, 10)
    ax1.triplot(Triangulation(1e3 * karkea.p[0], 1e3 * karkea.p[1],
                              karkea.t.T), color=HARMAA, linewidth=0.4)
    ax1.set(aspect="equal", xlabel="x (mm)", ylabel="y (mm)",
            title="kuvattu verkko")
    verkko = m.neljannes(a, 32, 32)
    kanta = fem.Basis(verkko, fem.ElementVector(fem.ElementTriP2()))
    lam, mu = lame_parameters(m.E_MODUULI, m.NU)
    lam = 2.0 * lam * mu / (lam + 2.0 * mu)
    k = linear_elasticity(lam, mu).assemble(kanta)
    oikea = fem.FacetBasis(verkko, kanta.elem, facets=verkko.facets_satisfying(
        lambda x: np.isclose(x[0], m.W)))
    f = fem.LinearForm(lambda v, w: m.VETO * v[0]).assemble(oikea)
    lukitut = np.concatenate([
        kanta.get_dofs(lambda x: np.isclose(x[0], 0.0)).all("u^1"),
        kanta.get_dofs(lambda x: np.isclose(x[1], 0.0)).all("u^2")])
    u = fem.solve(*fem.condense(k, f, D=lukitut))
    venyma = sym_grad(kanta.interpolate(u))
    sxx = 2.0 * mu * venyma[0, 0] + lam * (venyma[0, 0] + venyma[1, 1])
    solmuissa = kanta.with_element(fem.ElementTriP1()).project(sxx)
    tri = Triangulation(1e3 * verkko.p[0], 1e3 * verkko.p[1], verkko.t.T)
    kuva = ax2.tripcolor(tri, solmuissa / m.VETO, cmap=KARTTA,
                         shading="gouraud", rasterized=True)
    ax2.tricontour(tri, solmuissa / m.VETO, levels=[0.5, 1.5, 2.0, 2.5, 3.0],
                   colors="white", linewidths=0.5)
    ax2.set(aspect="equal", xlabel="x (mm)", title="σₓₓ / vetojännitys")
    fig.colorbar(kuva, ax=ax2, shrink=0.8)
    for ax in (ax1, ax2):
        ax.title.set_fontsize(8)
    tallenna(fig, polku)


def taipuma(polku: Path) -> None:
    m = lataa("09-kirjasto.py")
    import skfem as fem
    fig = uusi(4.2, 2.6)
    ax = fig.add_subplot()
    for el, nimi, vari, merkki in ((fem.ElementTriP1(), "lineaarinen (P1)",
                                    HARMAA, "s"),
                                   (fem.ElementTriP2(), "toinen aste (P2)",
                                    KOROSTUS, "o")):
        n, osuus = [], []
        for nx, ny in ((10, 1), (20, 2), (40, 4), (80, 8)):
            maara, d = m.taipuma(nx, ny, el)
            n.append(maara)
            osuus.append(100.0 * d / m.teoria)
        ax.semilogx(n, osuus, merkki + "-", color=vari, markersize=3.5,
                    linewidth=1, label=nimi)
    ax.axhline(100, color=VAALEA, linewidth=0.8, linestyle="--")
    ax.set(xlabel="vapausasteita", ylabel="taipuma, % palkkiteoriasta",
           ylim=(0, 110))
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, polku)


# --- Luku 10 ------------------------------------------------------------

def moodit(polku: Path) -> None:
    import pienfem
    import skfem as fem
    from scipy.sparse.linalg import eigsh
    from skfem.models.poisson import laplace, mass
    fig = uusi(5.6, 2.1, dpi=180)
    akselit = fig.subplots(1, 3)
    oma = pienfem.l_alue(12)
    verkko = fem.MeshTri(np.ascontiguousarray(oma.pisteet.T),
                         np.ascontiguousarray(oma.kolmiot.T))
    kanta = fem.Basis(verkko, fem.ElementTriP2())
    vapaat = kanta.complement_dofs(kanta.get_dofs())
    k = laplace.assemble(kanta)[vapaat][:, vapaat]
    mm = mass.assemble(kanta)[vapaat][:, vapaat]
    arvot, vektorit = eigsh(k, k=3, M=mm, sigma=0.0, which="LM")
    tri = kolmiointi(oma)
    for i, ax in enumerate(akselit):
        kaikki = np.zeros(kanta.N)
        kaikki[vapaat] = vektorit[:, i]
        u = kaikki[kanta.nodal_dofs[0]]          # arvot kärkisolmuissa
        u /= u[np.argmax(np.abs(u))]
        ax.tripcolor(tri, u, cmap=KARTTA, shading="gouraud", vmin=-1, vmax=1,
                     rasterized=True)
        ax.tricontour(tri, u, levels=[-0.75, -0.5, -0.25, 0.25, 0.5, 0.75],
                      colors="white", linewidths=0.4)
        ax.set(aspect="equal",
               title=f"λ = {arvot[i]:.2f}".replace(".", ","))
        ax.title.set_fontsize(8)
        ax.set_xticks([])
        ax.set_yticks([])
    tallenna(fig, polku)


def lampeneminen(polku: Path) -> None:
    m = lataa("10-lampo.py")
    fig = uusi(4.4, 2.6)
    ax = fig.add_subplot()
    t = np.full(len(m.x), m.T_ILMA)
    ajat, keski, kuumin = [0.0], [m.T_ILMA], [m.T_ILMA]
    for askel in range(1, m.ASKELIA + 1):
        t = m.hajotelma.solve(m.m @ t + m.DT * m.b)
        ajat.append(askel * m.DT)
        varasto = float(np.sum(m.m @ (t - m.T_ILMA)))
        keski.append(m.T_ILMA + varasto / (m.RHO_C * m.LEVEYS * m.KORKEUS))
        kuumin.append(float(t.max()))
    aika = np.array(ajat)
    malli = m.T_ILMA + m.teho_sisaan / (m.H * m.KORKEUS) * (
        1.0 - np.exp(-aika / m.aikavakio))
    ax.plot(aika / 60, kuumin, color=VAALEA, linewidth=1,
            label="kuumin kohta")
    ax.plot(aika / 60, keski, color=KOROSTUS, linewidth=1.3,
            label="levyn keskilämpötila")
    ax.plot(aika / 60, malli, color=HARMAA, linewidth=1, linestyle="--",
            label="yhden lämpötilan malli")
    ax.set(xlabel="aika (min)", ylabel="lämpötila (°C)")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, polku)


# --- Luku 11 ------------------------------------------------------------

def verkot(polku: Path) -> None:
    import pienfem
    m = lataa("11-laatu.py")
    fig = uusi(5.6, 2.3, dpi=180)
    ax1, ax2 = fig.subplots(1, 2)
    for ax, verkko, nimi in ((ax1, pienfem.suorakulmio(4, 16),
                              "suorat kulmat"),
                             (ax2, m.siirretty(4, 16), "siirretyt rivit")):
        ax.triplot(kolmiointi(verkko), color=HARMAA, linewidth=0.5)
        ax.set(aspect="equal", xlim=(0, 1), ylim=(0, 0.5),
               title=f"{nimi}: suurin kulma {m.kulmat(verkko)[1]:.0f}°")
        ax.title.set_fontsize(8)
        ax.set_xticks([])
        ax.set_yticks([])
    tallenna(fig, polku)


def porrastus(polku: Path) -> None:
    m = lataa("11-porrastus.py")
    fig = uusi(5.6, 2.6, dpi=180)
    ax1, ax2 = fig.subplots(1, 2)
    v = m.porrasta(m.perus, 0.25)
    ax1.triplot(Triangulation(v.p[0], v.p[1], v.t.T), color=HARMAA,
                linewidth=0.35)
    ax1.set(aspect="equal", title=f"porrastettu verkko, {v.p.shape[1]} "
            "solmua")
    ax1.title.set_fontsize(8)
    ax1.set_xticks([-1, 0, 1])
    ax1.set_yticks([-1, 0, 1])
    tas, por = [], []
    t = m.perus
    for koko in (0.5, 0.25, 0.125, 0.0625):
        t = t.refined()
        tas.append(m.l2_virhe(t))
        por.append(m.l2_virhe(m.porrasta(m.perus, koko)))
    ax2.loglog(*zip(*tas, strict=True), "s-", color=HARMAA, markersize=3,
               linewidth=1, label="tasainen")
    ax2.loglog(*zip(*por, strict=True), "o-", color=KOROSTUS, markersize=3,
               linewidth=1, label="porrastettu")
    ax2.set(xlabel="solmuja", ylabel="L2-virhe")
    ax2.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


# --- Luku 12 ------------------------------------------------------------

def validointi(polku: Path) -> None:
    m = lataa("12-validointi.py")
    fig = uusi(5.6, 2.6)
    ax1, ax2 = fig.subplots(1, 2)
    x = 1e3 * m.ANTURIT
    ax1.fill_between(x, m.alin, m.ylin, color=VAALEA, alpha=0.5,
                     label="malli, h = 10 ± 3")
    ax1.plot(x, m.malli(m.h_sovitettu, 100.0), color=KOROSTUS, linewidth=1,
             label=f"sovitettu h = {m.h_sovitettu:.1f}".replace(".", ","))
    ax1.errorbar(x, m.mitattu, yerr=0.3, fmt="o", color="black",
                 markersize=3, linewidth=0.8, label="mittaus")
    ax1.set(xlabel="anturin paikka (mm)", ylabel="lämpötila (°C)",
            title="tyvi 100 °C: kalibrointi")
    ax1.legend(frameon=False, fontsize=7)
    ax2.plot(x, m.malli(m.h_sovitettu, 300.0), color=KOROSTUS, linewidth=1,
             label="sama malli")
    ax2.errorbar(x, m.koe(300.0, siemen=2), yerr=0.3, fmt="o", color="black",
                 markersize=3, linewidth=0.8, label="mittaus")
    ax2.set(xlabel="anturin paikka (mm)", title="tyvi 300 °C: ennuste")
    ax2.legend(frameon=False, fontsize=7)
    for ax in (ax1, ax2):
        ax.title.set_fontsize(8)
    tallenna(fig, polku)


def richardson(polku: Path) -> None:
    m = lataa("12-gci.py")
    fig = uusi(4.2, 2.6)
    ax = fig.add_subplot()
    ns = np.array([8, 16, 32, 64])
    arvot = np.array([m.tulokset[int(n)][0] for n in ns])
    h = 1.0 / ns
    p = math.log2((arvot[2] - arvot[1]) / (arvot[3] - arvot[2]))
    raja = arvot[3] + (arvot[3] - arvot[2]) / (2.0**p - 1.0)
    tihea = np.linspace(0.0, h[0], 100)
    c = (raja - arvot[3]) / h[3] ** p
    ax.plot(tihea, raja - c * tihea**p, color=VAALEA, linewidth=1,
            linestyle="--", label=f"raja − C·h^{p:.2f}".replace(".", ","))
    ax.plot(h, arvot, "o", color=KOROSTUS, markersize=4, label="lasketut")
    ax.plot([0], [raja], "*", color="black", markersize=8,
            label="ekstrapoloitu")
    ax.set(xlabel="ruudun sivu h", ylabel="ratkaisun integraali")
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    valitut = set(sys.argv[2:])
    for nimi, piirra in (
            ("ripa", ripa), ("tase", tase), ("dimensioton", dimensioton),
            ("levy", levy), ("ftcs", ftcs), ("porras", porras),
            ("biot", biot), ("kieli", kieli), ("kalvo", kalvo),
            ("hattu", hattu), ("l-alue", l_alue), ("lammitin", lammitin),
            ("kertaluvut", kertaluvut), ("uloke", uloke), ("reika", reika),
            ("taipuma", taipuma), ("moodit", moodit),
            ("lampeneminen", lampeneminen), ("verkot", verkot),
            ("porrastus", porrastus), ("validointi", validointi),
            ("richardson", richardson)):
        if not valitut or nimi in valitut:
            piirra(kohde / f"{nimi}.png")


if __name__ == "__main__":
    main()
