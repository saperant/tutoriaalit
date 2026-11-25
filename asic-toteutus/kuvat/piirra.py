"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
lukujen testattujen esimerkkien funktioilla ja vakioilla samoilla
siemenillä tai luetaan esimerkkien testatuista tulosteista, joten
kuvat näyttävät samat ajot kuin tulosteet. Kolme kuvaa (solun
rakenne, antennisääntö ja kotelot) on periaatepiirroksia.
"""

import importlib.util
import math
import random
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Polygon, Rectangle

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))

from liberty import lue, taulukko  # noqa: E402
from sta import Analyysi, Rajoitteet  # noqa: E402
from synteesi import syntetisoi  # noqa: E402

KOROSTUS = "#546676"
TOINEN = "#B07A2A"
VIRHE = "#B4532A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
HAALEA = "#E4EAEC"
TUMMA = "#1F2A2E"
VIHREA = "#5E8A62"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 8
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}
LAMPO = LinearSegmentedColormap.from_list(
    "lampo", ["#F4F6F7", "#E9D9B4", TOINEN, VIRHE, "#5A1F12"])
AIKA = LinearSegmentedColormap.from_list(
    "aika", [KOROSTUS, "#9FB0A0", "#E3C989", TOINEN, VIRHE])


def lataa(nimi: str) -> ModuleType:
    """Lataa esimerkin moduulina ajamatta sen main-funktiota."""
    tiedosto = ESIMERKIT / nimi
    spec = importlib.util.spec_from_file_location(
        tiedosto.stem.replace("-", "_") + "_kuva", tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = moduuli
    spec.loader.exec_module(moduuli)
    return moduuli


def uusi(leveys: float = 4.6, korkeus: float = 2.5) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)
    print(polku.name)


def tyhja(ax: Axes) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def laatikko(ax: Axes, x: float, y: float, w: float, h: float,
             vari: str, **kw: Any) -> None:
    ax.add_patch(Rectangle((x, y), w, h, facecolor=vari,
                           edgecolor=kw.pop("reuna", "none"), **kw))


# --- luku 2 -----------------------------------------------------------

def solu(kohde: Path) -> None:
    """Invertterisolun pohjakuva ja poikkileikkaus (periaatepiirros)."""
    fig = uusi(4.6, 2.6)
    ax = fig.add_subplot(1, 2, 1)
    tyhja(ax)
    ax.set_xlim(-0.3, 4.6)
    ax.set_ylim(-0.5, 8.6)
    ax.set_aspect("equal")
    ax.set_title("pohjakuva ylhäältä", fontsize=8)
    kaivo, diff_n, diff_p = "#F1E6C8", "#9CC3A1", "#E3B58F"
    poly, met = "#B4532A", "#7E97AD"
    laatikko(ax, 0.0, 4.2, 3.0, 4.0, kaivo, reuna=TOINEN, lw=0.6,
             linestyle="--")
    laatikko(ax, 0.6, 5.0, 1.8, 1.8, diff_p)          # PMOS, leveämpi
    laatikko(ax, 0.6, 1.4, 1.8, 1.0, diff_n)          # NMOS
    laatikko(ax, 1.35, 0.9, 0.3, 6.4, poly)           # hila
    laatikko(ax, 0.0, 7.3, 3.0, 0.9, met, alpha=0.85)  # VDD
    laatikko(ax, 0.0, -0.2, 3.0, 0.9, met, alpha=0.85)  # VSS
    laatikko(ax, 0.7, 6.3, 0.4, 1.3, met, alpha=0.85)   # lähde -> VDD
    laatikko(ax, 0.7, 0.4, 0.4, 1.5, met, alpha=0.85)   # lähde -> VSS
    laatikko(ax, 1.9, 1.6, 0.4, 4.8, met, alpha=0.85)   # nielut -> Y
    for x, y in [(0.9, 5.4), (0.9, 6.3), (0.9, 1.7), (2.1, 5.4),
                 (2.1, 6.2), (2.1, 1.9)]:
        laatikko(ax, x - 0.1, y - 0.1, 0.2, 0.2, TUMMA)
    for teksti, y, vari in [("VDD", 7.75, "white"), ("VSS", 0.25, "white")]:
        ax.text(2.6, y, teksti, color=vari, ha="center", va="center",
                fontsize=7)
    selitteet = [("n-kaivo", kaivo, 7.6), ("p-diffuusio (PMOS)", diff_p,
                                           6.6),
                 ("polypii (hila)", poly, 5.6), ("metalli 1", met, 4.6),
                 ("n-diffuusio (NMOS)", diff_n, 3.6),
                 ("kontakti", TUMMA, 2.6)]
    for teksti, vari, y in selitteet:
        laatikko(ax, 3.3, y, 0.25, 0.25, vari, reuna=HARMAA, lw=0.3)
        ax.text(3.65, y + 0.12, teksti.split(" (")[0], fontsize=6,
                va="center")
    ax.annotate("A", (1.5, 4.0), (0.4, 3.6), fontsize=7,
                arrowprops={"arrowstyle": "-", "lw": 0.5})
    ax.annotate("Y", (2.1, 3.9), (2.55, 3.4), fontsize=7,
                arrowprops={"arrowstyle": "-", "lw": 0.5})
    ax.plot([-0.15, -0.15], [-0.2, 8.2], color=HARMAA, lw=0.6)
    ax.text(-0.25, 4.0, "solun korkeus", rotation=90, va="center",
            ha="right", fontsize=6, color=HARMAA)

    ax = fig.add_subplot(1, 2, 2)
    tyhja(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.6)
    ax.set_title("poikkileikkaus: NMOS ja PMOS", fontsize=8)
    laatikko(ax, 0, 0.5, 10, 3.2, "#EDEFF0")               # p-alusta
    ax.text(0.2, 0.8, "p-tyypin piialusta", fontsize=6, color=HARMAA)
    laatikko(ax, 5.3, 1.6, 4.5, 2.1, kaivo)                 # n-kaivo
    ax.text(9.6, 1.8, "n-kaivo", fontsize=6, color=TOINEN, ha="right")
    for x0, vari in [(0.6, diff_n), (5.9, diff_p)]:
        laatikko(ax, x0, 3.0, 1.2, 0.7, vari)
        laatikko(ax, x0 + 2.0, 3.0, 1.2, 0.7, vari)
        laatikko(ax, x0 + 1.2, 3.7, 0.8, 0.08, TUMMA)       # hilaoksidi
        laatikko(ax, x0 + 1.2, 3.78, 0.8, 0.6, poly)        # hila
        for dx in (0.45, 2.45):                              # kontaktit
            laatikko(ax, x0 + dx, 3.7, 0.3, 1.1, TUMMA)
            laatikko(ax, x0 + dx - 0.3, 4.8, 0.9, 0.45, met)
    ax.text(1.2, 3.3, "n+", fontsize=6, ha="center", va="center")
    ax.text(3.2, 3.3, "n+", fontsize=6, ha="center", va="center")
    ax.text(6.5, 3.3, "p+", fontsize=6, ha="center", va="center")
    ax.text(8.5, 3.3, "p+", fontsize=6, ha="center", va="center")
    ax.annotate("hila (polypii)", (2.2, 4.3), (1.2, 6.4), fontsize=6,
                arrowprops={"arrowstyle": "-", "lw": 0.5})
    ax.annotate("hilaoksidi", (7.5, 3.74), (6.3, 6.4), fontsize=6,
                arrowprops={"arrowstyle": "-", "lw": 0.5})
    ax.annotate("kanava", (2.2, 3.6), (1.6, 2.2), fontsize=6,
                arrowprops={"arrowstyle": "-", "lw": 0.5})
    ax.text(5.0, 5.6, "metalli 1", fontsize=6, ha="center", color=KOROSTUS)
    ax.text(5.0, 7.6, "ylemmät metallit ja eristeet", fontsize=6,
            ha="center", color=HARMAA)
    ax.plot([0, 10], [7.2, 7.2], color=VAALEA, lw=0.5, linestyle=":")
    tallenna(fig, kohde / "solu.png")


def ajurit(kohde: Path) -> None:
    """Viive kuorman funktiona eri ajureilla ja NLDM käyräparvena."""
    m = lataa("02-ajurit.py")
    kuormat = [0.002 + 0.002 * i for i in range(40)]
    fig = uusi(4.6, 2.3)
    ax = fig.add_subplot(1, 2, 1)
    for nimi, vari, tyyli in [("INV_X1", VIRHE, "-"),
                              ("BUF_X1", TOINEN, "--"),
                              ("BUF_X4", KOROSTUS, "-")]:
        ax.plot([k * 1000 for k in kuormat],
                [m.viive(nimi, 0.10, k)[0] * 1000 for k in kuormat],
                color=vari, linestyle=tyyli, lw=1.3, label=nimi)
    ax.axvline(80, color=VAALEA, lw=0.8, linestyle=":")
    ax.text(79, 20, "max_capacitance", rotation=90, fontsize=6,
            ha="right", va="bottom", color=HARMAA)
    ax.set_xlabel("kuorma (fF)")
    ax.set_ylabel("viive (ps)")
    ax.set_title("ajurin koko, tulon siirtymä 0,10 ns", fontsize=8)
    ax.legend(frameon=False, fontsize=7)

    ax = fig.add_subplot(1, 2, 2)
    kirjasto = lue(ESIMERKIT / "opetus.lib")
    y = kirjasto.yksi("cell", "INV_X1").yksi("pin", "Y")
    t = taulukko(kirjasto, y.kaikki("timing")[0].yksi("cell_rise",
                                                       "nldm_3x3"))
    varit = [KOROSTUS, TOINEN, VIRHE]
    for slew, vari in zip(t.indeksi1, varit, strict=True):
        ax.plot([k * 1000 for k in kuormat[:25]],
                [t.arvo(slew, k) * 1000 for k in kuormat[:25]],
                color=vari, lw=1.2,
                label=f"siirtymä {slew:.2f} ns".replace(".", ","))
        ax.plot([c * 1000 for c in t.indeksi2],
                [t.arvo(slew, c) * 1000 for c in t.indeksi2], "o",
                color=vari, ms=3.5)
    ax.set_xlabel("kuorma (fF)")
    ax.set_title("INV_X1: cell_rise-taulukko", fontsize=8)
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, kohde / "ajurit.png")


# --- luku 3 -----------------------------------------------------------

def etuliiteverkot() -> dict[str, list[list[tuple[int, int]]]]:
    """Tasot, joissa (bitti, lähde): solmu yhdistää bitin ja lähteen."""
    n = 8
    ripple = [[(i, i - 1)] for i in range(1, n)]
    ks = [[(i, i - 2 ** t) for i in range(2 ** t, n)] for t in range(3)]
    bk = [[(i, i - 2 ** t) for i in range(n) if (i + 1) % 2 ** (t + 1) == 0]
          for t in range(3)]
    bk.append([(5, 3)])
    bk.append([(2, 1), (4, 3), (6, 5)])
    return {"ripple-carry": ripple, "Brent–Kung": bk, "Kogge–Stone": ks}


def etuliite(kohde: Path) -> None:
    fig = uusi(4.6, 2.5)
    for k, (nimi, tasot) in enumerate(etuliiteverkot().items()):
        ax = fig.add_subplot(1, 3, k + 1)
        tyhja(ax)
        syvyys = len(tasot)
        ax.set_xlim(-0.6, 7.6)
        ax.set_ylim(-7.6, 0.9)
        for i in range(8):
            ax.plot([7 - i, 7 - i], [0, -7.2], color=HAALEA, lw=0.8,
                    zorder=1)
            ax.text(7 - i, 0.35, str(i), ha="center", fontsize=6,
                    color=HARMAA)
        askel = 7.0 / max(syvyys, 7) if nimi == "ripple-carry" else 1.4
        for t, taso in enumerate(tasot):
            y = -(t + 1) * askel
            for bitti, lahde in taso:
                ax.plot([7 - lahde, 7 - bitti], [y + askel, y],
                        color=KOROSTUS, lw=0.8, zorder=2)
                ax.plot([7 - bitti], [y], "o", color=TUMMA, ms=3.5,
                        zorder=3)
        solmuja = sum(len(t) for t in tasot)
        ax.set_title(f"{nimi}\n{solmuja} solmua, syvyys {syvyys}",
                     fontsize=7)
    tallenna(fig, kohde / "etuliite.png")


def ppa(kohde: Path) -> None:
    """Pinta-ala ja viive testatusta tulosteesta."""
    rivit = (ESIMERKIT / "03-arkkitehtuuri.odotettu").read_text(
        "utf-8").splitlines()[1:]
    fig = uusi(3.4, 2.3)
    ax = fig.add_subplot()
    nimet = {"ripple": "ripple-carry", "bk": "Brent–Kung",
             "ks": "Kogge–Stone", "bk, ABC:n oletus":
             "Brent–Kung,\nABC:n oletus"}
    for rivi in rivit:
        osat = rivi.rsplit(maxsplit=4)
        nimi, ala, viive = osat[0].strip(), float(osat[2]), float(osat[3])
        oletus = "ABC" in nimi
        ax.plot([ala], [viive], "s" if oletus else "o",
                color=VIRHE if oletus else KOROSTUS, ms=6)
        dx, dy, ha = (60, 0.0, "left")
        if oletus:
            dx, dy, ha = (0, -0.75, "center")
        elif nimi == "ripple":
            dx, dy, ha = (0, 0.25, "center")
        ax.text(ala + dx, viive + dy, nimet[nimi], fontsize=7, ha=ha,
                va="center")
    ax.set_xlabel("pinta-ala (µm²)")
    ax.set_ylabel("kriittinen polku (ns)")
    ax.set_xlim(2500, 4400)
    ax.set_ylim(0, 4.3)
    tallenna(fig, kohde / "ppa.png")


# --- luku 4 -----------------------------------------------------------

def marginaalit(kohde: Path) -> None:
    """Kertojan loppupisteiden pahimmat asetusmarginaalit."""
    tulos = syntetisoi([ESIMERKIT / "kertoja.v"], "kertoja")
    polut = Analyysi(tulos, Rajoitteet(jakso=2.0, sisaan=0.3)).polut()
    pahin: dict[str, float] = {}
    for p in polut:
        if p.lajia == "asetus":
            pahin[p.loppu] = min(pahin.get(p.loppu, 9.9), p.marginaali)
    tulot = sorted((n, v) for n, v in pahin.items() if n.startswith("tulo"))
    tulot.sort(key=lambda nv: int(nv[0][5:-1]))
    fig = uusi(4.6, 2.2)
    ax = fig.add_subplot()
    xs = range(len(tulot))
    ax.bar(xs, [v for _, v in tulot],
           color=[VIRHE if v < 0 else KOROSTUS for _, v in tulot])
    ax.axhline(0, color=TUMMA, lw=0.6)
    ax.set_xticks(list(xs), [n[5:-1] for n, _ in tulot])
    ax.set_xlabel("loppupiste: tulorekisterin bitti")
    ax.set_ylabel("asetusmarginaali (ns)")
    muut = [v for n, v in pahin.items() if not n.startswith("tulo")]
    ax.text(0.99, 0.95, f"rekisterit a_r ja b_r: {min(muut):+.2f} ns "
            "tai enemmän".replace(".", ","), transform=ax.transAxes,
            ha="right", va="top", fontsize=7, color=HARMAA)
    tallenna(fig, kohde / "marginaalit.png")


# --- luku 6 -----------------------------------------------------------

def kattavuus(kohde: Path) -> None:
    """Vikakattavuus satunnaisvektorien määrän funktiona (c17)."""
    m = lataa("06-vikasim.py")
    johtimet = m.TULOT + list(m.PORTIT)
    viat = [(j, a) for j in johtimet for a in (0, 1)]

    def kayra(siemen: int, n: int = 16) -> list[float]:
        rng = random.Random(siemen)
        v = [{t: rng.randint(0, 1) for t in m.TULOT} for _ in range(n)]
        return [100 * len(m.havaitut(v[:k], viat)) / len(viat)
                for k in range(1, n + 1)]

    fig = uusi(3.6, 2.2)
    ax = fig.add_subplot()
    xs = list(range(1, 17))
    muut = [kayra(s) for s in range(2, 42)]
    ala = [min(k[i] for k in muut) for i in range(16)]
    yla = [max(k[i] for k in muut) for i in range(16)]
    ax.fill_between(xs, ala, yla, color=HAALEA, label="40 muuta siementä")
    ax.plot(xs, kayra(1), "o-", color=KOROSTUS, ms=3, lw=1.2,
            label="tulosteen ajo (siemen 1)")
    ax.axhline(100, color=VAALEA, lw=0.6, linestyle=":")
    ax.set_xlabel("satunnaisia vektoreita")
    ax.set_ylabel("vikakattavuus (%)")
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, kohde / "kattavuus.png")


# --- luku 7 -----------------------------------------------------------

def _sijoittelu(ax: Axes, m: ModuleType, solut: list[str],
                johtimet: list[list[str]], paikat: dict[str, Any],
                tyypit: dict[str, str], otsikko: str) -> None:
    tyhja(ax)
    ax.set_xlim(-1.6, m.PAIKKOJA + 0.6)
    ax.set_ylim(-0.7, m.RIVEJA - 0.3)
    ax.set_aspect("equal")
    for y in range(m.RIVEJA):
        laatikko(ax, -0.45, y - 0.42, m.PAIKKOJA - 0.1, 0.84, "#F4F6F7")
    for j in johtimet:
        cx = sum(paikat[n][0] for n in j) / len(j)
        cy = sum(paikat[n][1] for n in j) / len(j)
        for n in j:
            ax.plot([paikat[n][0], cx], [paikat[n][1], cy], color=HARMAA,
                    lw=0.35, alpha=0.55, zorder=2)
    for n in solut:
        x, y = paikat[n]
        kiikku = tyypit[n].startswith("DFF")
        laatikko(ax, x - 0.36, y - 0.3, 0.72, 0.6,
                 KOROSTUS if kiikku else VAALEA, zorder=3)
    for n, (x, y) in paikat.items():
        if n not in tyypit:
            ax.plot([x], [y], ">" if x < 0 else "s", color=TOINEN, ms=2.5,
                    zorder=3)
    ax.set_title(otsikko, fontsize=8)


def sijoittelu(kohde: Path) -> None:
    m = lataa("07-sijoittelu.py")
    netlista = syntetisoi([ESIMERKIT / "laskuri.v"], "laskuri").moduuli()
    solut, johtimet, kiinteat = m.verkot(netlista)
    tyypit = {n: netlista["cells"][n]["type"] for n in solut}
    _, _, alussa = m.alkusijoittelu(solut, kiinteat, random.Random(1))
    historia: list[tuple[float, float]] = []
    alku, loppu, lopussa = m.jaahdytys(solut, johtimet, kiinteat,
                                       historia=historia)
    fig = uusi(4.6, 2.0)
    _sijoittelu(fig.add_subplot(1, 2, 1), m, solut, johtimet, alussa,
                tyypit, f"satunnainen alku: HPWL {alku:.0f}")
    _sijoittelu(fig.add_subplot(1, 2, 2), m, solut, johtimet, lopussa,
                tyypit, f"jäähdytyksen jälkeen: HPWL {loppu:.0f}")
    tallenna(fig, kohde / "sijoittelu.png")

    fig = uusi(4.6, 2.1)
    ax = fig.add_subplot(1, 2, 1)
    ax.plot(range(len(historia)), [h for _, h in historia],
            color=KOROSTUS, lw=1.2)
    ax.set_xlabel("lämpötila-askel (lämpötila laskee →)")
    ax.set_ylabel("HPWL")
    ax.set_title("jäähdytyksen kulku", fontsize=8)
    ax.set_ylim(0, 300)
    ax = fig.add_subplot(1, 2, 2)
    kartta = m.ruuhka(johtimet, lopussa)
    kuva = ax.imshow(kartta, cmap=LAMPO, origin="lower", aspect="equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("ruuhka (RUDY)", fontsize=8)
    fig.colorbar(kuva, ax=ax, shrink=0.8, label="johdintiheys")
    tallenna(fig, kohde / "ruuhka.png")


# --- luku 8 -----------------------------------------------------------

def kellopuu(kohde: Path) -> None:
    m = lataa("08-kellopuu.py")
    rakenteet = [("ketju", m.ketju(), False),
                 ("H-puu", m.h_puu(500.0, 500.0, 1000.0, 2), True),
                 ("puskuroitu H-puu",
                  m.h_puu(500.0, 500.0, 1000.0, 2, True), True)]
    fig = uusi(4.6, 2.05)
    viiveet = [[t * 1e12 for t in m.viiveet(j)] for _, j, _ in rakenteet]
    pienin = min(min(v) for v in viiveet)
    suurin = max(max(v) for v in viiveet)
    kuva = None
    for k, ((nimi, juuri, h), v) in enumerate(zip(rakenteet, viiveet,
                                                  strict=True)):
        ax = fig.add_subplot(1, 3, k + 1)
        tyhja(ax)
        ax.set_xlim(-60, 1060)
        ax.set_ylim(-60, 1060)
        ax.set_aspect("equal")
        laatikko(ax, 0, 0, 1000, 1000, "#F7F8F9", reuna=VAALEA, lw=0.5)
        kiikut: list[Any] = []

        def kulje(s: Any, h: bool = h, ax: Axes = ax,
                  kiikut: list[Any] = kiikut) -> None:
            if s.kiikku:
                kiikut.append(s)
            for lapsi in s.lapset:
                if h:        # H-muoto: ensin vaakaan, sitten pystyyn
                    ax.plot([s.x, lapsi.x, lapsi.x], [s.y, s.y, lapsi.y],
                            color=TUMMA, lw=0.9, zorder=2)
                else:
                    ax.plot([s.x, s.x, lapsi.x], [s.y, lapsi.y, lapsi.y],
                            color=TUMMA, lw=0.9, zorder=2)
                kulje(lapsi)
            if s.puskuri:
                ax.plot([s.x], [s.y], "^", color=TOINEN, ms=5, zorder=4)

        kulje(juuri)
        kuva = ax.scatter([s.x for s in kiikut], [s.y for s in kiikut],
                          c=v, cmap=AIKA, vmin=pienin, vmax=suurin, s=22,
                          zorder=3, edgecolors=TUMMA, linewidths=0.3)
        ax.plot([juuri.x], [juuri.y], "D", color=VIRHE, ms=4, zorder=5)
        ax.set_title(f"{nimi}\nvinous {max(v) - min(v):.0f} ps",
                     fontsize=7)
    assert kuva is not None
    fig.colorbar(kuva, ax=fig.axes, shrink=0.75, label="saapumisaika (ps)")
    tallenna(fig, kohde / "kellopuu.png")


def reititys(kohde: Path) -> None:
    m = lataa("08-reititys.py")
    korkeus, leveys = len(m.ALUE), len(m.ALUE[0])
    varit = {"A": KOROSTUS, "B": TOINEN, "C": VIHREA}
    fig = uusi(4.6, 3.3)

    def pohja(ax: Axes, otsikko: str) -> None:
        tyhja(ax)
        ax.set_xlim(-0.5, leveys - 0.5)
        ax.set_ylim(korkeus - 0.5, -0.5)
        ax.set_aspect("equal")
        for y, rivi in enumerate(m.ALUE):
            for x, c in enumerate(rivi):
                laatikko(ax, x - 0.5, y - 0.5, 1, 1,
                         HARMAA if c == "#" else "#F7F8F9", reuna="white",
                         lw=0.5)
        ax.set_title(otsikko, fontsize=8)

    # Aaltorintama johtimelle B, kun A on jo reititetty (1 kerros).
    varatut: dict[Any, str] = {}
    for nimi, (a, b) in m.JOHTIMET.items():
        varatut[(*a, 0)] = varatut[(*b, 0)] = nimi.lower()
    a, b = m.JOHTIMET["A"]
    aalto_a: dict[Any, int] = {}
    reitti_a = m.reitita(varatut, (*a, 0), (*b, 0), 1, aalto_a)
    ax = fig.add_subplot(2, 2, 1)
    pohja(ax, "A: aaltorintama ja reitti")
    for (x, y, _), d in aalto_a.items():
        ax.text(x, y, str(d), ha="center", va="center", fontsize=4.5,
                color=HARMAA)
    ax.plot([r[0] for r in reitti_a], [r[1] for r in reitti_a],
            color=varit["A"], lw=3.5, alpha=0.35, solid_capstyle="round")
    for r in reitti_a[1:-1]:
        varatut[r] = "A"
    a, b = m.JOHTIMET["B"]
    aalto_b: dict[Any, int] = {}
    tulos = m.reitita(varatut, (*a, 0), (*b, 0), 1, aalto_b)
    assert tulos is None
    ax = fig.add_subplot(2, 2, 2)
    pohja(ax, "B yhdellä kerroksella: ei reittiä")
    ax.plot([r[0] for r in reitti_a], [r[1] for r in reitti_a],
            color=varit["A"], lw=2.2, alpha=0.75, solid_capstyle="round")
    for (x, y, _), d in aalto_b.items():
        ax.text(x, y, str(d), ha="center", va="center", fontsize=4.5,
                color=TOINEN)
    ax.plot([a[0], b[0]], [a[1], b[1]], "o", color=varit["B"], ms=5)

    kaikki, virheet = m.reitita_kaikki(2)
    assert not virheet
    for z in (0, 1):
        ax = fig.add_subplot(2, 2, 3 + z)
        pohja(ax, f"kaksi kerrosta: metalli {z + 1}")
        for (x, y, kerros), nimi in kaikki.items():
            if kerros != z:
                continue
            iso = nimi.upper()
            laatikko(ax, x - 0.32, y - 0.32, 0.64, 0.64, varit[iso],
                     alpha=0.85)
            toinen = kaikki.get((x, y, 1 - z), "").upper()
            if toinen == iso:                 # läpivienti
                laatikko(ax, x - 0.2, y - 0.2, 0.4, 0.4, "white")
            if nimi.islower():                # nasta
                ax.text(x, y, iso, ha="center", va="center", fontsize=5,
                        color=TUMMA if toinen == iso else "white")
    tallenna(fig, kohde / "reititys.png")


# --- luku 10 ----------------------------------------------------------

def drc(kohde: Path) -> None:
    m = lataa("10-drc.py")
    rikkeet = m.drc(m.KUVIO)
    fig = uusi(4.6, 1.9)
    ax = fig.add_subplot()
    ax.set_aspect("equal")
    ax.set_xlim(-0.15, 4.4)
    ax.set_ylim(-0.25, 1.25)
    for k in m.KUVIO:
        mukana = any(k.nimi in r for r in rikkeet)
        via = k.kerros == "via1"
        laatikko(ax, k.x0, k.y0, k.x1 - k.x0, k.y1 - k.y0,
                 TUMMA if via else "#7E97AD",
                 reuna=VIRHE if mukana else "none", lw=1.0, zorder=3 if via
                 else 2)
    ax.annotate("väli 0,12 < 0,14", (1.0, 0.20), (0.55, 0.62), fontsize=7,
                color=VIRHE, arrowprops={"arrowstyle": "->", "lw": 0.6,
                                         "color": VIRHE})
    ax.annotate("leveys 0,10 < 0,14", (3.10, 0.75), (3.3, 0.45),
                fontsize=7, color=VIRHE,
                arrowprops={"arrowstyle": "->", "lw": 0.6, "color": VIRHE})
    ax.annotate("reunus 0,02 < 0,05", (2.41, 0.7), (1.25, 1.05),
                fontsize=7, color=VIRHE,
                arrowprops={"arrowstyle": "->", "lw": 0.6, "color": VIRHE})
    for k in m.KUVIO:
        if k.kerros == "met1":
            ax.text(k.x1 + 0.03 if k.nimi[-1] in "AB" else k.x0,
                    (k.y0 + k.y1) / 2 if k.nimi[-1] in "AB" else k.y1 + 0.05,
                    k.nimi[-1], fontsize=7, va="center" if k.nimi[-1] in
                    "AB" else "bottom")
    ax.set_xlabel("µm")
    ax.set_ylabel("µm")
    tallenna(fig, kohde / "drc.png")


def ir(kohde: Path) -> None:
    m = lataa("10-ir.py")
    n = 11
    kulmat = {(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)}
    reunat = {(i, j) for i in range(0, n, 2) for j in (0, n - 1)} | {
        (j, i) for i in range(0, n, 2) for j in (0, n - 1)}
    tapaukset = [("4 kulmanastaa", kulmat, 0.5), ("reunarengas", reunat,
                                                   0.5),
                 ("rengas ja leveät liuskat", reunat, 0.2)]
    fig = uusi(4.6, 1.9)
    kuva = None
    for k, (nimi, syotot, r) in enumerate(tapaukset):
        v = m.ratkaise(n, r, 0.006, syotot)
        pudotus = [[(m.V_SYOTTO - x) * 1000 for x in rivi] for rivi in v]
        ax = fig.add_subplot(1, 3, k + 1)
        kuva = ax.imshow(pudotus, cmap=LAMPO, vmin=0, vmax=105,
                         origin="lower")
        ax.plot([x for x, _ in syotot], [y for _, y in syotot], "s",
                color=KOROSTUS, ms=2.5)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        pahin = max(max(rivi) for rivi in pudotus)
        ax.set_title(f"{nimi}\npahin {pahin:.0f} mV", fontsize=7)
    assert kuva is not None
    fig.colorbar(kuva, ax=fig.axes, shrink=0.75, label="pudotus (mV)")
    tallenna(fig, kohde / "ir.png")


def antenni(kohde: Path) -> None:
    """Antennisääntö poikkileikkauksena (periaatepiirros)."""
    fig = uusi(4.6, 1.7)
    met, poly, diff = "#7E97AD", "#B4532A", "#9CC3A1"
    for k, otsikko in enumerate(["metalli 1 etsataan: varaus purkautuu "
                                 "hilan läpi",
                                 "korjaus: hyppy ylemmälle kerrokselle"]):
        ax = fig.add_subplot(1, 2, k + 1)
        tyhja(ax)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5.2)
        ax.set_title(otsikko, fontsize=7)
        laatikko(ax, 0, 0.3, 10, 1.0, "#EDEFF0")
        laatikko(ax, 0.6, 1.3, 1.0, 0.07, TUMMA)
        laatikko(ax, 0.6, 1.37, 1.0, 0.45, poly)
        ax.text(1.1, 0.75, "hila", fontsize=6, ha="center")
        laatikko(ax, 8.0, 0.9, 1.4, 0.4, diff)
        ax.text(8.7, 0.55, "ajurin diffuusio", fontsize=6, ha="center")
        laatikko(ax, 0.95, 1.82, 0.3, 0.7, TUMMA)
        if k == 0:
            laatikko(ax, 0.6, 2.52, 6.6, 0.45, met)
            ax.text(3.9, 2.74, "pitkä metalli 1", fontsize=6, ha="center",
                    va="center", color="white")
            for x in (1.6, 3.0, 4.4, 5.8):
                ax.annotate("", (x, 3.0), (x + 0.3, 4.3),
                            arrowprops={"arrowstyle": "->", "lw": 0.6,
                                        "color": VIRHE})
                ax.text(x + 0.35, 4.35, "+", color=VIRHE, fontsize=8)
            ax.annotate("", (1.1, 1.1), (1.1, 1.8),
                        arrowprops={"arrowstyle": "->", "lw": 1.0,
                                    "color": VIRHE})
            ax.text(7.6, 3.2, "ei vielä\nyhteyttä", fontsize=6,
                    color=HARMAA, ha="center")
        else:
            laatikko(ax, 0.6, 2.52, 1.2, 0.45, met)
            laatikko(ax, 1.35, 2.97, 0.3, 0.6, TUMMA)
            laatikko(ax, 1.0, 3.57, 7.9, 0.45, "#5E7890")
            ax.text(5.0, 3.79, "metalli 2: tehdään myöhemmin", fontsize=6,
                    ha="center", va="center", color="white")
            laatikko(ax, 8.4, 2.97, 0.3, 0.6, TUMMA)
            laatikko(ax, 8.0, 2.52, 1.2, 0.45, met)
            laatikko(ax, 8.55, 1.3, 0.3, 1.22, TUMMA)
            ax.text(3.2, 2.1, "hilaan kytketty\nmetalli jää lyhyeksi",
                    fontsize=6, color=HARMAA)
    tallenna(fig, kohde / "antenni.png")


# --- luku 11 ----------------------------------------------------------

def kiekko(kohde: Path) -> None:
    """Sama satunnainen virhejoukko kahdella piirikoolla."""
    m = lataa("11-saanto.py")
    sade = m.KIEKKO_MM / 2
    rng = random.Random(2)
    ala_cm2 = math.pi * sade ** 2 / 100
    virheet = []
    while len(virheet) < round(m.VIRHETIHEYS * ala_cm2):
        x, y = rng.uniform(-sade, sade), rng.uniform(-sade, sade)
        if x * x + y * y <= sade * sade:
            virheet.append((x, y))
    fig = uusi(4.6, 2.5)
    for k, ala in enumerate([100, 400]):
        sivu = math.sqrt(ala)
        ax = fig.add_subplot(1, 2, k + 1)
        tyhja(ax)
        ax.set_xlim(-sade - 4, sade + 4)
        ax.set_ylim(-sade - 4, sade + 4)
        ax.set_aspect("equal")
        ax.add_patch(Circle((0, 0), sade, facecolor="#F4F6F7",
                            edgecolor=HARMAA, lw=0.6))
        n = int(sade // sivu) + 1
        ehjia = kaikki = 0
        for i in range(-n, n):
            for j in range(-n, n):
                x0, y0 = i * sivu, j * sivu
                kulmat = [(x0, y0), (x0 + sivu, y0), (x0, y0 + sivu),
                          (x0 + sivu, y0 + sivu)]
                if any(x * x + y * y > sade * sade for x, y in kulmat):
                    continue
                viallinen = any(x0 <= x < x0 + sivu and y0 <= y < y0 + sivu
                                for x, y in virheet)
                kaikki += 1
                ehjia += not viallinen
                laatikko(ax, x0 + 0.4, y0 + 0.4, sivu - 0.8, sivu - 0.8,
                         "#E7B8A6" if viallinen else "#C9D8CB")
        ax.plot([x for x, _ in virheet], [y for _, y in virheet], ".",
                color=VIRHE, ms=2)
        ax.set_title(f"{ala} mm²: {ehjia}/{kaikki} ehjää "
                     f"({100 * ehjia / kaikki:.0f} %)", fontsize=8)
    tallenna(fig, kohde / "kiekko.png")


def saanto(kohde: Path) -> None:
    m = lataa("11-saanto.py")
    alat = [4 + 2 * i for i in range(249)]
    fig = uusi(4.6, 2.2)
    ax = fig.add_subplot(1, 2, 1)
    ax.plot(alat, [100 * m.saanto(a)[0] for a in alat], color=KOROSTUS,
            lw=1.2, label="Poisson")
    ax.plot(alat, [100 * m.saanto(a)[1] for a in alat], color=TOINEN,
            lw=1.2, linestyle="--", label="Murphy")
    ax.set_xlabel("piirin ala (mm²)")
    ax.set_ylabel("saanto (%)")
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=7)
    ax = fig.add_subplot(1, 2, 2)
    hinnat = [m.KIEKON_HINTA / (m.piireja_kiekolla(a) * m.saanto(a)[1])
              for a in alat]
    ax.plot(alat, hinnat, color=KOROSTUS, lw=1.2)
    for a in [4, 25, 100, 400]:
        h = m.KIEKON_HINTA / (m.piireja_kiekolla(a) * m.saanto(a)[1])
        ax.plot([a], [h], "o", color=VIRHE, ms=3.5)
    ax.set_yscale("log")
    ax.set_xlabel("piirin ala (mm²)")
    ax.set_ylabel("€ / toimiva piiri")
    tallenna(fig, kohde / "saanto.png")


def kotelo(kohde: Path) -> None:
    """Lankabondaus ja flip-chip poikkileikkauksena (periaatepiirros)."""
    fig = uusi(4.6, 1.6)
    pii, alusta, juote = "#7E97AD", "#C9D8CB", "#B8C4C8"
    for k, otsikko in enumerate(["lankabondaus", "flip-chip"]):
        ax = fig.add_subplot(1, 2, k + 1)
        tyhja(ax)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)
        ax.set_title(otsikko, fontsize=8)
        laatikko(ax, 0.5, 1.0, 9, 0.6, alusta)
        ax.text(5, 1.3, "kotelon alusta", fontsize=6, ha="center",
                va="center")
        for x in (1.5, 3.25, 5.0, 6.75, 8.5):
            ax.add_patch(Circle((x, 0.6), 0.35, facecolor=juote,
                                edgecolor=HARMAA, lw=0.4))
        if k == 0:
            laatikko(ax, 3.0, 1.6, 4, 0.9, pii)
            ax.text(5, 2.05, "piiri", fontsize=6, ha="center",
                    va="center", color="white")
            ax.text(5, 2.75, "aktiivipinta ylöspäin", fontsize=6,
                    ha="center", color=HARMAA)
            for x0, x1 in ((3.2, 1.3), (6.8, 8.7)):
                xs = [x0 + (x1 - x0) * t / 20 for t in range(21)]
                ys = [2.5 + 1.6 * math.sin(math.pi * t / 20) * (1 - t / 40)
                      - 0.9 * (t / 20) for t in range(21)]
                ax.plot(xs, ys, color=TOINEN, lw=1.0)
            ax.text(5, 3.9, "lanka: 1–3 nH", fontsize=6, ha="center",
                    color=TOINEN)
            ax.add_patch(Polygon([(0.9, 1.6), (2.2, 4.6), (7.8, 4.6),
                                  (9.1, 1.6)], closed=True, fill=False,
                                 edgecolor=VAALEA, lw=0.6))
        else:
            laatikko(ax, 3.0, 2.15, 4, 0.9, pii)
            ax.text(5, 2.6, "piiri", fontsize=6, ha="center",
                    va="center", color="white")
            ax.text(8.6, 1.87, "aktiivipinta\nalaspäin", fontsize=6,
                    ha="center", va="center", color=HARMAA)
            for x in (3.4, 4.2, 5.0, 5.8, 6.6):
                ax.add_patch(Circle((x, 1.87), 0.25, facecolor=TOINEN,
                                    edgecolor="none"))
            ax.text(5, 3.6, "juotoskuulat koko pinnalla: noin 0,1 nH",
                    fontsize=6, ha="center", color=TOINEN)
    tallenna(fig, kohde / "kotelo.png")


KUVAT = [solu, ajurit, etuliite, ppa, marginaalit, kattavuus, sijoittelu,
         kellopuu, reititys, drc, ir, antenni, kiekko, saanto, kotelo]


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    valitut = set(sys.argv[2:])
    for f in KUVAT:
        if not valitut or f.__name__ in valitut:
            f(kohde)


if __name__ == "__main__":
    main()
