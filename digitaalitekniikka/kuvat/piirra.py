"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py [HAKEMISTO]

Kuvat ovat versionhallinnassa, joten tätä ei ajeta testeissä. Piirit ja
luvut tulevat lukujen testatuista esimerkeistä (esimerkit/): summaimien
viiveet porttisimulaattorista ja Karnaugh-kartan ryhmät
Quine–McCluskeyn toteutuksesta.
"""

import contextlib
import importlib.util
import io
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch
from matplotlib.path import Path as Polku

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#6D4FA0"          # alueen Tietokonejärjestelmät väri
KOROSTUS_VAALEA = "#E4DCF0"
TOINEN = "#B07A2A"
TOINEN_VAALEA = "#F1E3CC"
HARMAA = "#5B6B70"
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
Piste = tuple[float, float]


def uusi(leveys: float, korkeus: float) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def tyhja(ax: Axes, x: Piste, y: Piste) -> None:
    ax.set_xlim(*x)
    ax.set_ylim(*y)
    ax.set_aspect("equal")
    ax.set_axis_off()


def lataa(tiedosto: str) -> ModuleType:
    """Lataa esimerkkiohjelman moduulina; sen tulosteet ohitetaan."""
    sys.path.insert(0, str(ESIMERKIT))
    nimi = "esimerkki_" + tiedosto.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(nimi, ESIMERKIT / tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    sys.modules[nimi] = moduuli
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(moduuli)
    return moduuli


# ---------------------------------------------------------------------
# Porttisymbolit

def johdin(ax: Axes, *pisteet: Piste, vari: str = MUSTE) -> None:
    xs, ys = zip(*pisteet, strict=True)
    ax.plot(xs, ys, color=vari, lw=1.0, solid_capstyle="round", zorder=1)


def piste(ax: Axes, p: Piste) -> None:
    ax.add_patch(Circle(p, 0.045, color=MUSTE, zorder=3))


def portti(ax: Axes, laji: str, x: float, y: float) -> tuple[list[Piste],
                                                              Piste]:
    """Piirtää portin, jonka runko alkaa kohdasta x ja keskilinja on y.
    Palauttaa tulojen ja lähdön liitäntäpisteet."""
    k = 0.3                                  # rungon puolikorkeus
    pohja = laji.removeprefix("N") if laji in ("NAND", "NOR") else laji
    pohja = {"XNOR": "XOR", "NOT": "NOT"}.get(pohja, pohja)
    invertoiva = laji in ("NOT", "NAND", "NOR", "XNOR")
    tyyli = {"facecolor": KOROSTUS_VAALEA, "edgecolor": MUSTE, "lw": 1.0,
             "zorder": 2}
    if pohja == "NOT":
        karki = x + 0.5
        ax.add_patch(PathPatch(Polku(
            [(x, y - k), (x, y + k), (karki, y), (x, y - k)],
            [Polku.MOVETO, Polku.LINETO, Polku.LINETO, Polku.CLOSEPOLY]),
            **tyyli))
        tulot = [(x, y)]
    elif pohja == "AND":
        kulma = np.linspace(np.pi / 2, -np.pi / 2, 24)
        kaari = [(x + 0.3 + k * np.cos(t), y + k * np.sin(t))
                 for t in kulma]
        pisteet = [(x, y - k), (x, y + k), *kaari, (x, y - k)]
        ax.add_patch(PathPatch(Polku(pisteet), **tyyli))
        karki = x + 0.3 + k
        tulot = [(x, y + 0.15), (x, y - 0.15)]
    else:                                    # OR ja XOR
        karki = x + 0.65
        runko = Polku(
            [(x, y + k), (x + 0.3, y + k), (x + 0.55, y + 0.18),
             (karki, y), (x + 0.55, y - 0.18), (x + 0.3, y - k),
             (x, y - k), (x + 0.14, y), (x, y + k)],
            [Polku.MOVETO, Polku.CURVE3, Polku.CURVE3, Polku.CURVE3,
             Polku.CURVE3, Polku.CURVE3, Polku.CURVE3, Polku.CURVE3,
             Polku.CURVE3])
        ax.add_patch(PathPatch(runko, **tyyli))
        if pohja == "XOR":
            kaari2 = Polku([(x - 0.09, y + k), (x + 0.05, y),
                            (x - 0.09, y - k)],
                           [Polku.MOVETO, Polku.CURVE3, Polku.CURVE3])
            ax.add_patch(PathPatch(kaari2, facecolor="none",
                                   edgecolor=MUSTE, lw=1.0, zorder=2))
        tulot = [(x + 0.05, y + 0.15), (x + 0.05, y - 0.15)]
    if invertoiva:
        ax.add_patch(Circle((karki + 0.055, y), 0.055, facecolor="white",
                            edgecolor=MUSTE, lw=1.0, zorder=3))
        karki += 0.11
    return tulot, (karki, y)


def portit(polku: Path) -> None:
    """Perusporttien symbolit ja lausekkeet."""
    fig = uusi(6.2, 1.1)
    ax = fig.add_subplot()
    tyhja(ax, (-0.2, 12.6), (-1.15, 0.45))
    lajit = [("NOT", "NOT", r"$\bar{a}$"), ("AND", "AND", r"$ab$"),
             ("OR", "OR", r"$a + b$"), ("XOR", "XOR", r"$a \oplus b$"),
             ("NAND", "NAND", r"$\overline{ab}$"),
             ("NOR", "NOR", r"$\overline{a + b}$"),
             ("XNOR", "XNOR", r"$\overline{a \oplus b}$")]
    for i, (laji, nimi, lauseke) in enumerate(lajit):
        x = 0.45 + 1.8 * i
        tulot, lahto = portti(ax, laji, x, 0.0)
        for t in tulot:
            johdin(ax, (x - 0.3, t[1]), t)
        johdin(ax, lahto, (lahto[0] + 0.3, 0.0))
        ax.text(x + 0.4, -0.56, nimi, ha="center", va="center",
                fontweight="bold", fontsize=8.5)
        ax.text(x + 0.4, -0.95, lauseke, ha="center", va="center",
                fontsize=8.5)
    fig.savefig(polku / "portit.png", metadata=METATIEDOT)


def nand_rakenteet(polku: Path) -> None:
    """NOT, AND ja OR pelkistä NAND-porteista (esimerkki 03-portit.py)."""
    fig = uusi(6.2, 1.75)
    ax = fig.add_subplot()
    tyhja(ax, (-0.3, 12.3), (-1.25, 0.95))

    # NOT: molemmat tulot samaan signaaliin.
    tulot, lahto = portti(ax, "NAND", 0.9, 0.0)
    johdin(ax, (0.0, 0.0), (0.5, 0.0))
    johdin(ax, (0.5, 0.15), (0.5, -0.15))
    piste(ax, (0.5, 0.0))
    for t in tulot:
        johdin(ax, (0.5, t[1]), t)
    johdin(ax, lahto, (lahto[0] + 0.4, 0.0))
    ax.text(-0.08, 0.0, "a", ha="right", va="center")
    ax.text(lahto[0] + 0.48, 0.0, r"$\bar{a}$", ha="left", va="center")
    ax.text(1.0, -1.0, "NOT", ha="center", fontweight="bold", fontsize=8.5)

    # AND: NAND ja NAND invertterinä.
    x0 = 4.0
    tulot, valilahto = portti(ax, "NAND", x0, 0.0)
    for nimi, t in zip("ab", tulot, strict=True):
        johdin(ax, (x0 - 0.45, t[1]), t)
        ax.text(x0 - 0.53, t[1], nimi, ha="right", va="center")
    tulot2, lahto = portti(ax, "NAND", x0 + 1.5, 0.0)
    haara = (x0 + 1.15, 0.0)
    johdin(ax, valilahto, haara)
    johdin(ax, (haara[0], 0.15), (haara[0], -0.15))
    piste(ax, haara)
    for t in tulot2:
        johdin(ax, (haara[0], t[1]), t)
    johdin(ax, lahto, (lahto[0] + 0.4, 0.0))
    ax.text(lahto[0] + 0.48, 0.0, r"$ab$", ha="left", va="center")
    ax.text(x0 + 1.0, -1.0, "AND", ha="center", fontweight="bold",
            fontsize=8.5)

    # OR: kumpikin tulo käännetään, sitten NAND (De Morgan).
    x0 = 9.0
    tulot3, lahto = portti(ax, "NAND", x0 + 1.5, 0.0)
    for nimi, y, t in (("a", 0.5, tulot3[0]), ("b", -0.5, tulot3[1])):
        tulot, ulos = portti(ax, "NAND", x0, y)
        johdin(ax, (x0 - 0.85, y), (x0 - 0.4, y))
        johdin(ax, (x0 - 0.4, y + 0.15), (x0 - 0.4, y - 0.15))
        piste(ax, (x0 - 0.4, y))
        for tulo in tulot:
            johdin(ax, (x0 - 0.4, tulo[1]), tulo)
        ax.text(x0 - 0.93, y, nimi, ha="right", va="center")
        johdin(ax, ulos, (x0 + 1.1, y), (x0 + 1.1, t[1]), t)
    johdin(ax, lahto, (lahto[0] + 0.4, 0.0))
    ax.text(lahto[0] + 0.48, 0.0, r"$a + b$", ha="left", va="center")
    ax.text(x0 + 0.8, -1.0, "OR", ha="center", fontweight="bold",
            fontsize=8.5)
    fig.savefig(polku / "nand-rakenteet.png", metadata=METATIEDOT)


# ---------------------------------------------------------------------
# CMOS-portit transistoreina

def transistori(ax: Axes, x: float, y: float, tyyppi: str,
                hila: str) -> tuple[Piste, Piste, Piste]:
    """Piirtää MOS-transistorin; kanava on pystyssä kohdassa x + 0.3.
    Palauttaa hilan, yläpään ja alapään liitäntäpisteet."""
    vari = TOINEN if tyyppi == "p" else KOROSTUS
    kanava = x + 0.3
    johdin(ax, (kanava, y + 0.45), (kanava, y + 0.22), (x + 0.1, y + 0.22),
           vari=vari)
    johdin(ax, (x + 0.1, y + 0.22), (x + 0.1, y - 0.22), vari=vari)
    johdin(ax, (x + 0.1, y - 0.22), (kanava, y - 0.22), (kanava, y - 0.45),
           vari=vari)
    ax.plot([x, x], [y - 0.2, y + 0.2], color=vari, lw=1.6, zorder=2)
    hilapaa = x
    if tyyppi == "p":                        # pMOS: pallo hilalla
        ax.add_patch(Circle((x - 0.07, y), 0.07, facecolor="white",
                            edgecolor=vari, lw=1.0, zorder=3))
        hilapaa = x - 0.14
    johdin(ax, (x - 0.5, y), (hilapaa, y), vari=MUSTE)
    ax.text(x - 0.58, y, hila, ha="right", va="center")
    return (x - 0.5, y), (kanava, y + 0.45), (kanava, y - 0.45)


def kisko(ax: Axes, x0: float, x1: float, y: float, nimi: str) -> None:
    johdin(ax, (x0, y), (x1, y))
    ax.text(x1 + 0.1, y, nimi, ha="left", va="center", fontsize=8)


def cmos(polku: Path) -> None:
    """Invertteri ja NAND-portti transistoritasolla."""
    fig = uusi(5.6, 3.0)
    ax = fig.add_subplot()
    tyhja(ax, (-1.2, 9.6), (-0.6, 5.0))

    # Invertteri.
    kisko(ax, -0.2, 1.4, 4.4, "VDD")
    kisko(ax, -0.2, 1.4, 0.0, "GND")
    _, ylos, pkesk = transistori(ax, 0.3, 3.3, "p", "a")
    _, nkesk, alas = transistori(ax, 0.3, 1.1, "n", "a")
    johdin(ax, ylos, (ylos[0], 4.4))
    johdin(ax, alas, (alas[0], 0.0))
    johdin(ax, pkesk, nkesk)
    johdin(ax, (pkesk[0], 2.2), (1.9, 2.2))
    piste(ax, (pkesk[0], 2.2))
    ax.text(2.0, 2.2, r"$y = \bar{a}$", ha="left", va="center")
    ax.text(0.6, -0.45, "invertteri", ha="center", fontweight="bold",
            fontsize=8.5)

    # NAND: pMOS rinnan ylhäällä, nMOS sarjassa alhaalla.
    x0 = 5.0
    kisko(ax, x0 - 0.5, x0 + 3.1, 4.4, "VDD")
    kisko(ax, x0 - 0.5, x0 + 3.1, 0.0, "GND")
    _, y1, a1 = transistori(ax, x0, 3.5, "p", "a")
    _, y2, a2 = transistori(ax, x0 + 1.8, 3.5, "p", "b")
    for p in (y1, y2):
        johdin(ax, p, (p[0], 4.4))
    lahto_y = 2.7
    johdin(ax, a1, (a1[0], lahto_y), (a2[0], lahto_y), a2)
    _, n1y, n1a = transistori(ax, x0, 1.9, "n", "a")
    _, n2y, n2a = transistori(ax, x0, 0.75, "n", "b")
    johdin(ax, (a1[0], lahto_y), n1y)
    johdin(ax, n1a, n2y)
    johdin(ax, n2a, (n2a[0], 0.0))
    piste(ax, (a1[0], lahto_y))
    piste(ax, (a2[0], lahto_y))
    johdin(ax, (a2[0], lahto_y), (x0 + 3.0, lahto_y))
    ax.text(x0 + 3.1, lahto_y, r"$y = \overline{ab}$", ha="left",
            va="center")
    ax.text(x0 + 1.1, -0.45, "NAND", ha="center", fontweight="bold",
            fontsize=8.5)
    ax.text(x0 + 2.75, 3.5, "ylösveto:\npMOS rinnan", ha="left",
            va="center", fontsize=7.5, color=TOINEN)
    ax.text(x0 + 0.75, 1.3, "alasveto:\nnMOS sarjassa", ha="left",
            va="center", fontsize=7.5, color=KOROSTUS)
    fig.savefig(polku / "cmos.png", metadata=METATIEDOT)


# ---------------------------------------------------------------------
# Kuvaajat esimerkkien datasta

def summainviive(polku: Path) -> None:
    """Summaimien asettumisaika bittimäärän funktiona (07-summaimet.py)."""
    m = lataa("07-summaimet.py")
    bitit = list(range(4, 33, 4))
    rca = [m.asettumisaika("rca", n) for n in bitit]
    cla = [m.asettumisaika("cla", n) for n in bitit]
    fig = uusi(4.4, 2.6)
    ax = fig.add_subplot()
    ax.plot(bitit, rca, "o-", color=TOINEN, label="ripple-carry")
    ax.plot(bitit, cla, "s-", color=KOROSTUS,
            label="lookahead, 4 bitin lohkot")
    ax.set_xlabel("summaimen leveys (bittiä)")
    ax.set_ylabel("asettumisaika (porttiviivettä)")
    ax.set_xticks(bitit)
    ax.set_ylim(0, 70)
    ax.grid(axis="y", color=HAALEA)
    ax.legend(frameon=False)
    fig.savefig(polku / "summainviive.png", metadata=METATIEDOT)


def karnaugh(polku: Path) -> None:
    """Karnaugh-kartta ja ryhmät esimerkistä 04-karnaugh.py."""
    qm = lataa("qm.py")
    gray = ["00", "01", "11", "10"]
    ykkoset, yhdentekevat = {2, 3, 5, 7}, set(range(10, 16))
    termit = qm.sievenna(4, sorted(ykkoset), sorted(yhdentekevat))
    fig = uusi(3.3, 2.7)
    ax = fig.add_subplot()
    tyhja(ax, (-1.2, 5.2), (-0.5, 5.0))
    for r, ab in enumerate(gray):
        ax.text(-0.25, 3.5 - r, ab, ha="right", va="center", color=HARMAA)
        for s, cd in enumerate(gray):
            if r == 0:
                ax.text(s + 0.5, 4.4, cd, ha="center", va="bottom",
                        color=HARMAA)
            ruutu = int(ab + cd, 2)
            ax.add_patch(FancyBboxPatch(
                (s, 3 - r), 1, 1, boxstyle="square,pad=0",
                facecolor="white", edgecolor=HARMAA, lw=0.6, zorder=1))
            merkki = ("1" if ruutu in ykkoset
                      else "x" if ruutu in yhdentekevat else "0")
            ax.text(s + 0.5, 3.5 - r, merkki, ha="center", va="center",
                    fontsize=11, zorder=4,
                    color=MUSTE if merkki == "1" else HARMAA)
            ax.text(s + 0.93, 3.07 - r, str(ruutu), ha="right",
                    va="bottom", fontsize=5.5, color=HARMAA, zorder=4)
    ax.text(-0.75, 4.4, "ab \\ cd", ha="center", va="bottom",
            color=HARMAA, fontsize=8)
    varit = [(KOROSTUS, KOROSTUS_VAALEA), (TOINEN, TOINEN_VAALEA)]
    for (reuna, tausta), termi in zip(varit, termit, strict=False):
        ruudut = [m for m in range(16) if qm.kattaa(termi, m)]
        rivit = sorted({gray.index(f"{m:04b}"[:2]) for m in ruudut})
        sarakkeet = sorted({gray.index(f"{m:04b}"[2:]) for m in ruudut})
        # Ryhmä voi kiertää kartan reunan yli (rivit 00 ja 10 ovat
        # vierekkäin). Silloin se piirretään kahtena palana, jotka
        # jatkuvat kartan reunan ohi.
        assert sarakkeet == list(range(sarakkeet[0], sarakkeet[-1] + 1))
        x, lev = sarakkeet[0] + 0.08, len(sarakkeet) - 0.16
        if rivit == list(range(rivit[0], rivit[-1] + 1)):
            palat = [(4 - rivit[-1] - 1 + 0.08, len(rivit) - 0.16)]
        else:
            assert rivit == [0, 3]
            palat = [(3.08, 1.17), (-0.25, 1.17)]
        for y, kork in palat:
            ax.add_patch(FancyBboxPatch(
                (x, y), lev, kork,
                boxstyle="round,pad=0,rounding_size=0.25",
                facecolor=tausta, edgecolor=reuna, lw=1.4, alpha=0.75,
                zorder=2))
        nimi = qm.lauseke([termi]).replace("'", "′")
        ax.text(4.25, palat[0][0] + palat[0][1] / 2, nimi, ha="left",
                va="center", color=reuna, fontweight="bold")
    fig.savefig(polku / "karnaugh.png", metadata=METATIEDOT)


def main() -> None:
    polku = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    for piirra in (portit, nand_rakenteet, cmos, summainviive, karnaugh):
        piirra(polku)


if __name__ == "__main__":
    main()
