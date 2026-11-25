"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle

KOROSTUS = "#9A6524"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def tyhja(ax: Axes) -> None:
    """Kaaviokuva ilman akseleita, mittasuhteet säilyttäen."""
    ax.set_aspect("equal")
    ax.axis("off")


def venn_joukot(polku: Path) -> None:
    """Luvun Joukot ja funktiot esimerkki: Python- ja C-osaajat."""
    python = {"Aino", "Olli", "Pekka", "Sanna"}
    c_kieli = {"Olli", "Sanna", "Timo"}
    kaikki = python | c_kieli | {"Ulla"}
    fig = Figure(figsize=(3.6, 2.2), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    tyhja(ax)
    ax.add_patch(Rectangle((-2.9, -1.6), 5.8, 3.2, fill=False,
                           edgecolor=HARMAA, linewidth=0.8))
    for x, vari in ((-0.75, KOROSTUS), (0.75, HARMAA)):
        ax.add_patch(Circle((x, 0), 1.3, facecolor=vari, alpha=0.18,
                            edgecolor="none"))
        ax.add_patch(Circle((x, 0), 1.3, fill=False, edgecolor=vari,
                            linewidth=1.2))
    ax.text(-1.6, 1.25, "A: Python", ha="center", color=KOROSTUS)
    ax.text(1.6, 1.25, "B: C", ha="center", color=HARMAA)
    ax.text(-2.75, -1.45, "U", color=HARMAA)
    alueet = ((-1.3, sorted(python - c_kieli)), (0.0, sorted(python & c_kieli)),
              (1.3, sorted(c_kieli - python)))
    for x, nimet in alueet:
        ax.text(x, 0, "\n".join(nimet), ha="center", va="center", fontsize=8)
    ulkona = sorted(kaikki - (python | c_kieli))
    ax.text(2.35, -1.3, ", ".join(ulkona), ha="center", fontsize=8)
    ax.set(xlim=(-3.0, 3.0), ylim=(-1.7, 1.7))
    tallenna(fig, polku)


def funktiot(polku: Path) -> None:
    """Luvun Joukot ja funktiot neljä funktiota nuolikaavioina."""
    tapaukset: tuple[tuple[str, Callable[[int], int], int, str], ...] = (
        ("3x mod 8", lambda x: 3 * x % 8, 8, "bijektio"),
        ("2x mod 8", lambda x: 2 * x % 8, 8, "ei kumpikaan"),
        ("x // 2", lambda x: x // 2, 4, "surjektio"),
        ("x + 1", lambda x: x + 1, 9, "injektio"),
    )
    fig = Figure(figsize=(6.6, 2.9), dpi=200, layout="constrained")
    for ax, (nimi, f, maali, laji) in zip(fig.subplots(1, 4), tapaukset,
                                          strict=True):
        ax.axis("off")
        osumat = Counter(f(x) for x in range(8))

        def y_a(x: int) -> float:
            return 8.0 - x

        def y_b(v: int, maali: int = maali) -> float:
            return 4.5 + (maali - 1) / 2 - v   # sarake keskitetty

        for x in range(8):
            ax.annotate("", xy=(0.88, y_b(f(x))), xytext=(0.12, y_a(x)),
                        arrowprops={"arrowstyle": "->", "color": HARMAA,
                                    "linewidth": 0.7})
            ax.text(0.0, y_a(x), str(x), ha="center", va="center",
                    fontsize=8)
        for v in range(maali):
            ehto_rikki = osumat[v] != 1
            ax.text(1.0, y_b(v), str(v), ha="center", va="center",
                    fontsize=8, color=KOROSTUS if ehto_rikki else "black",
                    fontweight="bold" if ehto_rikki else "normal")
        ax.set(xlim=(-0.2, 1.2), ylim=(-0.3, 9.6))
        ax.set_title(f"x ↦ {nimi}\n{laji}", fontsize=8.5)
    tallenna(fig, polku)


def kasvu(polku: Path) -> None:
    """Tavallisimmat kasvunopeudet logaritmisilla akseleilla."""
    fig = Figure(figsize=(4.4, 2.9), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    n = np.logspace(0.3, 4, 300)
    kayrat = (("log₂ n", np.log2(n), VAALEA, "-"),
              ("n", n, HARMAA, "-"),
              ("n log₂ n", n * np.log2(n), HARMAA, "--"),
              ("n²", n**2, KOROSTUS, "-"),
              ("2ⁿ", 2.0 ** np.minimum(n, 60), KOROSTUS, "--"))
    for nimi, y, vari, tyyli in kayrat:
        ax.loglog(n, y, color=vari, linestyle=tyyli, linewidth=1.2,
                  label=nimi)
    ax.set(xlabel="syötteen koko n", ylabel="askelia", ylim=(1, 1e10),
           xlim=(2, 1e4))
    ax.legend(frameon=False, fontsize=8, loc="upper left", ncols=2)
    tallenna(fig, polku)


def venn_inkluusio(polku: Path) -> None:
    """Luvun Kombinatoriikka esimerkki: luvut 1…1000, jaollisuus 2, 3, 5."""
    n = 1000
    alue: Counter[tuple[bool, bool, bool]] = Counter(
        (x % 2 == 0, x % 3 == 0, x % 5 == 0) for x in range(1, n + 1))
    fig = Figure(figsize=(3.8, 3.0), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    tyhja(ax)
    keskipisteet = {"A": (-0.6, 0.45), "B": (0.6, 0.45), "C": (0.0, -0.6)}
    for (x, y), vari in zip(keskipisteet.values(),
                            (KOROSTUS, HARMAA, "#2F5D8A"), strict=True):
        ax.add_patch(Circle((x, y), 1.0, facecolor=vari, alpha=0.15,
                            edgecolor="none"))
        ax.add_patch(Circle((x, y), 1.0, fill=False, edgecolor=vari,
                            linewidth=1.2))
    ax.text(-1.25, 1.5, f"A: jaollinen 2:lla\n|A| = {n // 2}", ha="center",
            color=KOROSTUS, fontsize=8)
    ax.text(1.25, 1.5, f"B: jaollinen 3:lla\n|B| = {n // 3}", ha="center",
            color=HARMAA, fontsize=8)
    ax.text(0.0, -1.95, f"C: jaollinen 5:llä, |C| = {n // 5}", ha="center",
            color="#2F5D8A", fontsize=8)
    paikat = {
        (True, False, False): (-1.05, 0.65), (False, True, False): (1.05, 0.65),
        (False, False, True): (0.0, -1.1), (True, True, False): (0.0, 0.8),
        (True, False, True): (-0.62, -0.25), (False, True, True): (0.62, -0.25),
        (True, True, True): (0.0, 0.1),
    }
    for avain, (x, y) in paikat.items():
        ax.text(x, y, str(alue[avain]), ha="center", va="center")
    ax.text(1.75, -1.45, f"ei mikään:\n{alue[(False, False, False)]}",
            ha="center", fontsize=8)
    ax.set(xlim=(-2.3, 2.5), ylim=(-2.1, 2.1))
    tallenna(fig, polku)


def hilapolut(polku: Path) -> None:
    """6 × 4 -ruudukon reittien määrä jokaisessa risteyksessä."""
    fig = Figure(figsize=(4.2, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    tyhja(ax)
    for x in range(7):
        ax.plot([x, x], [0, 4], color=VAALEA, linewidth=0.8)
    for y in range(5):
        ax.plot([0, 6], [y, y], color=VAALEA, linewidth=0.8)
    maara = [[1] * 7 for _ in range(5)]
    for y in range(1, 5):
        for x in range(1, 7):
            maara[y][x] = maara[y - 1][x] + maara[y][x - 1]
    for y in range(5):
        for x in range(7):
            ax.text(x, y, str(maara[y][x]), ha="center", va="center",
                    fontsize=7.5,
                    bbox={"boxstyle": "round,pad=0.15", "facecolor": "white",
                          "edgecolor": "none"})
    # Yksi reitti: O O Y O Y Y O O O Y (6 oikealle, 4 ylös).
    reitti = "OOYOYYOOOY"
    xs, ys = [0], [0]
    for askel in reitti:
        xs.append(xs[-1] + (askel == "O"))
        ys.append(ys[-1] + (askel == "Y"))
    ax.plot(xs, ys, color=KOROSTUS, linewidth=2.2, alpha=0.55, zorder=0.5)
    ax.text(-0.25, -0.45, "lähtö", ha="center", fontsize=8, color=HARMAA)
    ax.text(6.25, 4.4, "maali", ha="center", fontsize=8, color=HARMAA)
    ax.set(xlim=(-0.6, 6.7), ylim=(-0.7, 4.7))
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    for nimi, piirra in (("venn-joukot", venn_joukot),
                         ("funktiot", funktiot), ("kasvu", kasvu),
                         ("venn-inkluusio", venn_inkluusio),
                         ("hilapolut", hilapolut)):
        piirra(kohde / f"{nimi}.png")


if __name__ == "__main__":
    main()
