"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä.
"""

import math
import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure

KOROSTUS = "#9A6524"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
SININEN = "#2F5D8A"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}
Taulukko = npt.NDArray[np.float64]

# Epäsymmetrinen kuvio (F-kirjain yksikköneliössä): kierto, peilaus ja
# leikkaus näkyvät siitä paremmin kuin neliöstä.
F_KIRJAIN = np.array([
    [0.0, 0.25, 0.25, 0.55, 0.55, 0.25, 0.25, 0.7, 0.7, 0.0, 0.0],
    [0.0, 0.0, 0.45, 0.45, 0.65, 0.65, 0.8, 0.8, 1.0, 1.0, 0.0]])
NELIO = np.array([[0.0, 1.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 1.0, 0.0]])


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def kierto(asteet: float) -> Taulukko:
    t = math.radians(asteet)
    return np.array([[math.cos(t), -math.sin(t)],
                     [math.sin(t), math.cos(t)]])


def nuoli(ax: Axes, alku: tuple[float, float], loppu: tuple[float, float],
          vari: str, leveys: float = 1.4, tyyli: str = "-") -> None:
    ax.annotate("", xy=loppu, xytext=alku, zorder=5,
                arrowprops={"arrowstyle": "-|>", "color": vari,
                            "linewidth": leveys, "linestyle": tyyli,
                            "shrinkA": 0, "shrinkB": 0,
                            "mutation_scale": 9})


def ruudukko(ax: Axes, xlim: tuple[float, float],
             ylim: tuple[float, float]) -> None:
    """Tason akselit ja himmeä ruudukko, sama mittakaava molempiin."""
    ax.set_aspect("equal")
    ax.set(xlim=xlim, ylim=ylim)
    ax.set_xticks(range(math.ceil(xlim[0]), math.floor(xlim[1]) + 1))
    ax.set_yticks(range(math.ceil(ylim[0]), math.floor(ylim[1]) + 1))
    ax.grid(color=VAALEA, linewidth=0.4, alpha=0.6)
    ax.axhline(0, color=HARMAA, linewidth=0.6)
    ax.axvline(0, color=HARMAA, linewidth=0.6)
    ax.tick_params(labelsize=7, length=0)
    for s in ax.spines.values():
        s.set_visible(False)


def kuvio(ax: Axes, m: Taulukko, tayte: str = KOROSTUS,
          nuolet: bool = True) -> None:
    """Yksikköneliön ja F-kirjaimen kuva sekä kantavektorien kuvat."""
    n, f = m @ NELIO, m @ F_KIRJAIN
    ax.plot(n[0], n[1], color=HARMAA, linewidth=0.8, linestyle=":")
    ax.fill(f[0], f[1], facecolor=tayte, alpha=0.25, edgecolor=tayte,
            linewidth=1.0)
    if nuolet:
        nuoli(ax, (0, 0), (m[0, 0], m[1, 0]), KOROSTUS)
        nuoli(ax, (0, 0), (m[0, 1], m[1, 1]), SININEN)


def vektorit(polku: Path) -> None:
    """Summa nuolina ja projektio: rinteen suuntainen ja kohtisuora osa."""
    fig = Figure(figsize=(6.2, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    ruudukko(ax1, (-0.5, 4.6), (-0.5, 3.6))
    u, v = (3.0, 1.0), (1.0, 2.0)
    nuoli(ax1, (0, 0), u, KOROSTUS)
    nuoli(ax1, u, (u[0] + v[0], u[1] + v[1]), SININEN)
    nuoli(ax1, (0, 0), v, SININEN, 0.8, ":")
    nuoli(ax1, (0, 0), (4.0, 3.0), "black")
    ax1.text(1.7, 0.2, "u = (3, 1)", color=KOROSTUS, fontsize=8)
    ax1.text(3.65, 1.8, "v = (1, 2)", color=SININEN, fontsize=8)
    ax1.text(1.0, 2.1, "u + v = (4, 3)", fontsize=8, rotation=36.9)
    ax1.set_title("summa: nuolet peräkkäin", fontsize=8.5)

    # Luvun esimerkki: 100 kg:n kärry 30 asteen rinteessä.
    paino = np.array([0.0, -981.0])
    rinne = np.array([math.cos(math.radians(30)), math.sin(math.radians(30))])
    alas = (paino @ rinne) / (rinne @ rinne) * rinne
    kohti = paino - alas
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.plot([-900 * rinne[0], 500 * rinne[0]],
             [-900 * rinne[1], 500 * rinne[1]], color=HARMAA, linewidth=2.5)
    nuoli(ax2, (0, 0), (paino[0], paino[1]), "black")
    nuoli(ax2, (0, 0), (alas[0], alas[1]), KOROSTUS)
    nuoli(ax2, (alas[0], alas[1]), (paino[0], paino[1]), SININEN)
    ax2.plot([0], [0], "o", color="black", markersize=4)
    ax2.text(40, -620, "paino\n981 N", fontsize=8)
    ax2.text(-560, -90, f"projektio rinteelle\n{np.linalg.norm(alas):.1f} N",
             color=KOROSTUS, fontsize=8, ha="center")
    ax2.text(-640, -830, f"kohtisuora osa {np.linalg.norm(kohti):.1f} N",
             color=SININEN, fontsize=8, ha="center")
    ax2.text(330, 260, "rinne 30°", color=HARMAA, fontsize=8, rotation=30)
    ax2.set(xlim=(-1000, 600), ylim=(-1080, 380))
    ax2.set_title("projektio: voiman jako osiin", fontsize=8.5)
    tallenna(fig, polku)


def kuvaukset(polku: Path) -> None:
    """Luvun Matriisit peruskuvaukset yksikköneliölle ja F-kirjaimelle."""
    fig = Figure(figsize=(6.6, 2.1), dpi=200, layout="constrained")
    tapaukset = (("alkuperäinen", np.eye(2)),
                 ("kierto 30°", kierto(30)),
                 ("skaalaus (2; 0,5)", np.array([[2.0, 0.0], [0.0, 0.5]])),
                 ("leikkaus k = 0,5", np.array([[1.0, 0.5], [0.0, 1.0]])))
    for ax, (nimi, m) in zip(fig.subplots(1, 4), tapaukset, strict=True):
        ruudukko(ax, (-0.8, 2.3), (-0.4, 1.7))
        kuvio(ax, m)
        ax.set_title(nimi, fontsize=8.5)
    tallenna(fig, polku)


def jarjestys(polku: Path) -> None:
    """Skaalaus ja kierto kummassakin järjestyksessä."""
    fig = Figure(figsize=(5.4, 2.5), dpi=200, layout="constrained")
    s, r = np.array([[2.0, 0.0], [0.0, 1.0]]), kierto(90)
    for ax, (nimi, m) in zip(fig.subplots(1, 2),
                             (("R·S: ensin skaalaus, sitten kierto", r @ s),
                              ("S·R: ensin kierto, sitten skaalaus", s @ r)),
                             strict=True):
        ruudukko(ax, (-2.4, 1.4), (-0.4, 2.4))
        kuvio(ax, np.eye(2), HARMAA, nuolet=False)
        kuvio(ax, m)
        ax.set_title(nimi, fontsize=8.5)
    tallenna(fig, polku)


def suorat(polku: Path) -> None:
    """Kahden tuntemattoman yhtälöparin kolme tapausta."""
    fig = Figure(figsize=(6.4, 2.2), dpi=200, layout="constrained")
    x = np.array([-0.5, 3.0])
    tapaukset = (
        ("yksi ratkaisu", ("x + y = 2", 2 - x), ("x − y = 0", x)),
        ("ei ratkaisua", ("x + y = 2", 2 - x), ("x + y = 3", 3 - x)),
        ("äärettömästi ratkaisuja", ("x + y = 2", 2 - x),
         ("2x + 2y = 4", 2 - x)),
    )
    for ax, (nimi, (n1, y1), (n2, y2)) in zip(fig.subplots(1, 3), tapaukset,
                                               strict=True):
        ruudukko(ax, (-0.5, 3.0), (-0.5, 3.0))
        ax.plot(x, y1, color=HARMAA, linewidth=1.4, label=n1)
        ax.plot(x, y2, color=KOROSTUS, linewidth=1.4, label=n2,
                linestyle="--" if nimi.startswith("äär") else "-")
        if nimi == "yksi ratkaisu":
            ax.plot([1], [1], "o", color="black", markersize=4)
        ax.legend(frameon=False, fontsize=7, loc="upper right")
        ax.set_title(nimi, fontsize=8.5)
    tallenna(fig, polku)


def ehtoluku(polku: Path) -> None:
    """Leikkauspisteen herkkyys: kohtisuorat ja lähes yhdensuuntaiset
    suorat. Kulmaero on tuhatkertainen esimerkkiin verrattuna."""
    fig = Figure(figsize=(6.0, 2.7), dpi=200, layout="constrained")
    x = np.array([-2.0, 4.0])
    hairio = 0.2
    tapaukset = (("kohtisuorat suorat", np.array([[1.0, 1.0], [1.0, -1.0]]),
                  np.array([2.0, 0.0])),
                 ("lähes yhdensuuntaiset suorat",
                  np.array([[1.0, 1.0], [1.0, 1.1]]), np.array([2.0, 2.1])))
    for ax, (nimi, a, b) in zip(fig.subplots(1, 2), tapaukset, strict=True):
        ruudukko(ax, (-2.0, 4.0), (-1.5, 4.0))
        b2 = b + np.array([0.0, hairio])
        ax.plot(x, (b[0] - a[0, 0] * x) / a[0, 1], color=HARMAA,
                linewidth=1.3)
        ax.plot(x, (b[1] - a[1, 0] * x) / a[1, 1], color=KOROSTUS,
                linewidth=1.3)
        ax.plot(x, (b2[1] - a[1, 0] * x) / a[1, 1], color=KOROSTUS,
                linewidth=1.3, linestyle="--")
        p, p2 = np.linalg.solve(a, b), np.linalg.solve(a, b2)
        ax.plot([p[0]], [p[1]], "o", color="black", markersize=4)
        ax.plot([p2[0]], [p2[1]], "o", markerfacecolor="white",
                color="black", markersize=4)
        ax.set_title(f"{nimi}\nehtoluku {np.linalg.cond(a):.0f}",
                     fontsize=8.5)
    tallenna(fig, polku)


def determinantti(polku: Path) -> None:
    """Luvun Determinantti viisi kuvausta ja pinta-alan kerroin."""
    c, s = math.cos(math.radians(40)), math.sin(math.radians(40))
    tapaukset = (("skaalaus 2 × 3", [[2.0, 0.0], [0.0, 3.0]]),
                 ("kierto 40°", [[c, -s], [s, c]]),
                 ("leikkaus", [[1.0, 0.7], [0.0, 1.0]]),
                 ("peilaus", [[1.0, 0.0], [0.0, -1.0]]),
                 ("litistys", [[1.0, 2.0], [0.5, 1.0]]))
    fig = Figure(figsize=(6.8, 2.3), dpi=200, layout="constrained")
    for ax, (nimi, rivit) in zip(fig.subplots(1, 5), tapaukset, strict=True):
        m = np.array(rivit)
        ruudukko(ax, (-1.2, 3.2), (-1.3, 3.2))
        kuvio(ax, m)
        det = m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0]
        ax.set_title(f"{nimi}\ndet = {round(det, 3) + 0.0:.0f}", fontsize=8)
    tallenna(fig, polku)


def kannanvaihto(polku: Path) -> None:
    """Sama vektori v = (3, 1) kahdessa kannassa."""
    fig = Figure(figsize=(5.6, 2.6), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    b = np.array([[1.0, -1.0], [1.0, 1.0]])       # kantavektorit sarakkeina
    v = np.array([3.0, 1.0])
    c = np.linalg.solve(b, v)
    for ax in (ax1, ax2):
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set(xlim=(-1.6, 3.6), ylim=(-0.8, 2.8))
    for k in range(-2, 5):
        ax1.plot([k, k], [-0.8, 2.8], color=VAALEA, linewidth=0.5)
        ax1.plot([-1.6, 3.6], [k, k], color=VAALEA, linewidth=0.5)
        for suunta, toinen in ((b[:, 0], b[:, 1]), (b[:, 1], b[:, 0])):
            p0, p1 = k * toinen - 4 * suunta, k * toinen + 4 * suunta
            ax2.plot([p0[0], p1[0]], [p0[1], p1[1]], color=VAALEA,
                     linewidth=0.5)
    nuoli(ax1, (0, 0), (3, 0), KOROSTUS)
    nuoli(ax1, (3, 0), (3, 1), SININEN)
    nuoli(ax1, (0, 0), (1, 0), KOROSTUS, 2.4)
    nuoli(ax1, (0, 0), (0, 1), SININEN, 2.4)
    ax1.set_title("vakiokanta: v = 3 e₁ + 1 e₂", fontsize=8.5)
    b1, b2 = c[0] * b[:, 0], c[1] * b[:, 1]
    nuoli(ax2, (0, 0), (b1[0], b1[1]), KOROSTUS)
    nuoli(ax2, (b1[0], b1[1]), (b1[0] + b2[0], b1[1] + b2[1]), SININEN)
    nuoli(ax2, (0, 0), (b[0, 0], b[1, 0]), KOROSTUS, 2.4)
    nuoli(ax2, (0, 0), (b[0, 1], b[1, 1]), SININEN, 2.4)
    ax2.set_title(f"kanta B: v = {c[0]:.0f} b₁ − {abs(c[1]):.0f} b₂",
                  fontsize=8.5)
    for ax in (ax1, ax2):
        nuoli(ax, (0, 0), (3, 1), "black")
        ax.text(3.08, 1.05, "v", fontsize=9)
    tallenna(fig, polku)


def sovitus(polku: Path) -> None:
    """Luvun Pienimmän neliösumman sovitus kalibrointi ja jäännökset."""
    lampo = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
    jannite = np.array([0.502, 0.597, 0.708, 0.795, 0.903, 1.004, 1.091])
    a = np.column_stack([np.ones_like(lampo), lampo])
    x, *_ = np.linalg.lstsq(a, jannite, rcond=None)
    jaannos = (jannite - a @ x) * 1000
    fig = Figure(figsize=(6.2, 2.5), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    t = np.array([-3.0, 63.0])
    ax1.plot(t, x[0] + x[1] * t, color=KOROSTUS, linewidth=1.2,
             label=f"u = {x[0]:.4f} + {x[1]:.6f} T".replace(".", ","))
    ax1.plot(lampo, jannite, "o", color="black", markersize=3.5,
             label="mittaukset")
    ax1.set(xlabel="lämpötila T (°C)", ylabel="jännite u (V)")
    ax1.legend(frameon=False, fontsize=7.5)
    ax2.axhline(0, color=KOROSTUS, linewidth=1.0)
    ax2.vlines(lampo, 0, jaannos, color=HARMAA, linewidth=1.5)
    ax2.plot(lampo, jaannos, "o", color="black", markersize=3.5)
    ax2.set(xlabel="lämpötila T (°C)", ylabel="jäännös (mV)",
            ylim=(-9, 9))
    tallenna(fig, polku)


def ylisovitus(polku: Path) -> None:
    """Polynomisovitus asteilla 1, 5 ja 11 sekä virhe asteen funktiona."""
    rng = np.random.default_rng(2026)
    x = np.linspace(0.0, 1.0, 12)
    y = np.sin(2 * np.pi * x) + rng.normal(0.0, 0.1, x.size)
    testi_x = np.linspace(0.02, 0.98, 50)
    testi_y = np.sin(2 * np.pi * testi_x)
    tiheä = np.linspace(0.0, 1.0, 400)
    fig = Figure(figsize=(6.4, 2.7), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    ax1.plot(tiheä, np.sin(2 * np.pi * tiheä), color=VAALEA, linewidth=2.5,
             label="sin 2πx")
    for aste, vari, tyyli in ((1, HARMAA, ":"), (5, SININEN, "-"),
                              (11, KOROSTUS, "-")):
        k, *_ = np.linalg.lstsq(np.vander(x, aste + 1, increasing=True), y,
                                rcond=None)
        ax1.plot(tiheä, np.vander(tiheä, aste + 1, increasing=True) @ k,
                 color=vari, linestyle=tyyli, linewidth=1.1,
                 label=f"aste {aste}")
    ax1.plot(x, y, "o", color="black", markersize=3, label="mittaukset")
    ax1.set(xlabel="x", ylabel="y", ylim=(-1.8, 1.8))
    ax1.legend(frameon=False, fontsize=7, ncols=2, loc="lower left")
    opetus, testi = [], []
    asteet = range(1, 12)
    for aste in asteet:
        v = np.vander(x, aste + 1, increasing=True)
        k, *_ = np.linalg.lstsq(v, y, rcond=None)
        opetus.append(max(float(np.sqrt(np.mean((v @ k - y) ** 2))), 1e-4))
        testi.append(float(np.sqrt(np.mean(
            (np.vander(testi_x, aste + 1, increasing=True) @ k
             - testi_y) ** 2))))
    ax2.semilogy(asteet, opetus, "o-", color=HARMAA, markersize=3,
                 linewidth=1, label="opetusdata")
    ax2.semilogy(asteet, testi, "o-", color=KOROSTUS, markersize=3,
                 linewidth=1, label="uudet pisteet")
    ax2.set(xlabel="polynomin aste", ylabel="virhe (neliöllinen keskiarvo)",
            ylim=(8e-5, 2))
    ax2.set_xticks(list(asteet))
    ax2.legend(frameon=False, fontsize=7.5, loc="lower left")
    tallenna(fig, polku)


def ominaisvektorit(polku: Path) -> None:
    """Symmetrinen kuvaus: useimmat suunnat kääntyvät, kaksi ei."""
    a = np.array([[2.0, 1.0], [1.0, 2.0]])
    fig = Figure(figsize=(3.6, 3.4), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ruudukko(ax, (-3.2, 3.2), (-3.2, 3.2))
    kulmat = np.linspace(0.0, 2 * np.pi, 361)
    ympyra = np.vstack([np.cos(kulmat), np.sin(kulmat)])
    kuva = a @ ympyra
    ax.plot(ympyra[0], ympyra[1], color=HARMAA, linewidth=0.8)
    ax.plot(kuva[0], kuva[1], color=HARMAA, linewidth=0.8, linestyle="--")
    for asteet in range(0, 360, 30):
        x = kierto(asteet) @ np.array([1.0, 0.0])
        y = a @ x
        nuoli(ax, (x[0], x[1]), (y[0], y[1]), VAALEA, 0.9)
    r = 1 / math.sqrt(2)
    for v, lam, vari in ((np.array([r, r]), 3.0, KOROSTUS),
                         (np.array([-r, r]), 1.0, SININEN)):
        ax.plot([-4 * v[0], 4 * v[0]], [-4 * v[1], 4 * v[1]], color=vari,
                linewidth=0.6, linestyle=":")
        nuoli(ax, (0, 0), (lam * v[0], lam * v[1]), vari, 1.6)
        ax.plot([v[0]], [v[1]], "o", color=vari, markersize=3.5)
    ax.text(2.2, 1.55, "λ = 3", color=KOROSTUS, fontsize=8)
    ax.text(-1.55, 0.75, "λ = 1", color=SININEN, fontsize=8)
    tallenna(fig, polku)


def potenssi(polku: Path) -> None:
    """Potenssimenetelmän virhe Markovin ketjun esimerkissä."""
    p = np.array([[0.1, 0.3, 0.5, 0.6], [0.6, 0.3, 0.2, 0.2],
                  [0.2, 0.2, 0.2, 0.1], [0.1, 0.2, 0.1, 0.1]])
    arvot, vekt = np.linalg.eig(p)
    i = int(np.argmax(np.abs(arvot)))
    tasapaino = np.real(vekt[:, i]) / np.real(vekt[:, i]).sum()
    toinen = sorted(np.abs(arvot))[-2]
    v = np.ones(4) / 4
    virheet = []
    for _ in range(22):
        virheet.append(float(np.linalg.norm(v - tasapaino, 1)))
        v = p @ v
        v /= np.linalg.norm(v, 1)
    fig = Figure(figsize=(4.0, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    k = np.arange(22)
    ax.semilogy(k, virheet[0] * toinen ** k, color=VAALEA, linewidth=2.5,
                label=f"vakio · {toinen:.3f}ᵏ".replace(".", ","))
    ax.semilogy(k, virheet, "o", color=KOROSTUS, markersize=3,
                label="virhe (1-normi)")
    ax.set(xlabel="kierros k", ylabel="etäisyys tasapainojakaumasta")
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def pca(polku: Path) -> None:
    """Luvun Ominaisarvot anturidata ja pääakselit."""
    rng = np.random.default_rng(7)
    t = rng.uniform(-1.0, 1.0, 500)
    suunta = np.array([np.cos(np.radians(30)), np.sin(np.radians(30))])
    data = np.outer(t * 3.0, suunta) + rng.normal(0.0, 0.3, (500, 2))
    keski = data.mean(axis=0)
    c = (data - keski).T @ (data - keski) / (len(data) - 1)
    arvot, vekt = np.linalg.eigh(c)
    fig = Figure(figsize=(4.2, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.set_aspect("equal")
    ax.plot(data[:, 0], data[:, 1], ".", color=VAALEA, markersize=3)
    for j, vari in ((1, KOROSTUS), (0, SININEN)):
        v = vekt[:, j] * np.sign(vekt[0, j] if j else vekt[1, j])
        loppu = keski + 2 * math.sqrt(arvot[j]) * v
        nuoli(ax, (keski[0], keski[1]), (loppu[0], loppu[1]), vari, 1.8)
    ax.text(2.3, 2.1, "1. pääkomponentti", color=KOROSTUS, fontsize=8,
            ha="right")
    ax.text(-0.45, 0.75, "2. pääkomponentti", color=SININEN, fontsize=8,
            ha="right")
    ax.set(xlabel="kiihtyvyys x", ylabel="kiihtyvyys y")
    tallenna(fig, polku)


def svd(polku: Path) -> None:
    """A = U S V^T vaiheittain: kierto, venytys, kierto."""
    a = np.array([[2.0, 1.0], [0.5, 1.5]])
    _, s, vt = np.linalg.svd(a)
    # Hajotelman etumerkit ovat vapaat: valitaan ne niin, että V^T on
    # kierto (det = 1) ja v1 osoittaa oikealle.
    if np.linalg.det(vt) < 0:
        vt[1] = -vt[1]
    if vt[0, 0] < 0:
        vt = -vt
    kulmat = np.linspace(0.0, 2 * np.pi, 361)
    ympyra = np.vstack([np.cos(kulmat), np.sin(kulmat)])
    vaiheet = (("yksikköympyrä,\nsuunnat v₁ ja v₂", np.eye(2)),
               ("Vᵀ: kierto,\nv₁ ja v₂ akseleille", vt),
               ("Σ: venytys\nakselien suuntaan", np.diag(s) @ vt),
               ("U: kierto,\ntulos Ax", a))
    fig = Figure(figsize=(6.8, 2.3), dpi=200, layout="constrained")
    for ax, (nimi, m) in zip(fig.subplots(1, 4), vaiheet, strict=True):
        ruudukko(ax, (-2.8, 2.8), (-2.8, 2.8))
        k = m @ ympyra
        ax.fill(k[0], k[1], facecolor=VAALEA, alpha=0.35, edgecolor=HARMAA,
                linewidth=0.9)
        for j, vari in ((0, KOROSTUS), (1, SININEN)):
            p = m @ vt[j]
            nuoli(ax, (0, 0), (p[0], p[1]), vari, 1.6)
        ax.set_title(nimi, fontsize=8)
    tallenna(fig, polku)


def testikuva(n: int = 64) -> Taulukko:
    """Sama kuin esimerkissä 11-kuva.py."""
    y, x = np.mgrid[0:n, 0:n] / (n - 1)
    kuva = 0.25 + 0.5 * x
    kuva[(x - 0.35)**2 + (y - 0.4)**2 < 0.05] = 0.95
    kuva[(y > 0.72) & (y < 0.88) & (x > 0.45) & (x < 0.9)] = 0.05
    return np.asarray(kuva, dtype=np.float64)


def matala_aste(polku: Path) -> None:
    """Kuvan matala-asteiset approksimaatiot ja singulaariarvot."""
    kuva = testikuva()
    u, s, vt = np.linalg.svd(kuva, full_matrices=False)
    fig = Figure(figsize=(6.8, 3.3), dpi=200, layout="constrained")
    ruudut = fig.subplots(2, 4)
    tapaukset: tuple[int | None, ...] = (None, 1, 2, 4, 8, 16)
    for ax, k in zip(ruudut.flat, tapaukset, strict=False):
        ak = kuva if k is None else (u[:, :k] * s[:k]) @ vt[:k]
        ax.imshow(ak, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
        ax.axis("off")
        if k is None:
            ax.set_title("alkuperäinen, aste 17", fontsize=8)
        else:
            virhe = np.linalg.norm(kuva - ak) / np.linalg.norm(kuva)
            ax.set_title(f"k = {k}, virhe {virhe:.1%}".replace(".", ","),
                         fontsize=8)
    gs = ruudut[1, 2].get_gridspec()
    for ax in ruudut[1, 2:]:
        ax.remove()
    ax = fig.add_subplot(gs[1, 2:])
    ax.semilogy(range(1, 18), s[:17], "o-", color=KOROSTUS, markersize=3,
                linewidth=1)
    ax.set(xlabel="i", ylabel="singulaariarvo σᵢ")
    ax.tick_params(labelsize=7)
    tallenna(fig, polku)


def keskipiste(polku: Path) -> None:
    """Kierto oman keskipisteen ympäri: siirto, kierto, siirto."""
    # Luvun esimerkin 2 × 2 -hahmo, keskipiste (5, 3); F näyttää asennon.
    hahmo = 2 * F_KIRJAIN + np.array([[4.0], [2.0]])
    raami = 2 * NELIO + np.array([[4.0], [2.0]])

    def siirto(p: Taulukko, dx: float, dy: float) -> Taulukko:
        return p + np.array([[dx], [dy]])

    vaiheet = (("lähtö", lambda p: p),
               ("siirto origoon", lambda p: siirto(p, -5, -3)),
               ("kierto 90°", lambda p: kierto(90) @ siirto(p, -5, -3)),
               ("siirto takaisin",
                lambda p: siirto(kierto(90) @ siirto(p, -5, -3), 5, 3)))
    fig = Figure(figsize=(6.8, 2.0), dpi=200, layout="constrained")
    for ax, (nimi, f) in zip(fig.subplots(1, 4), vaiheet, strict=True):
        ruudukko(ax, (-2.5, 7.0), (-1.8, 4.8))
        h, r = f(hahmo), f(raami)
        ax.plot(r[0], r[1], color=HARMAA, linewidth=0.8, linestyle=":")
        ax.fill(h[0], h[1], facecolor=KOROSTUS, alpha=0.3,
                edgecolor=KOROSTUS, linewidth=1.0)
        keski = f(np.array([[5.0], [3.0]]))
        ax.plot(keski[0], keski[1], "+", color="black", markersize=6)
        ax.set_title(nimi, fontsize=8.5)
    tallenna(fig, polku)


def syvyys(polku: Path) -> None:
    """Syvyyspuskurin arvo etäisyyden funktiona kahdella lähitasolla."""
    fig = Figure(figsize=(4.2, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    kauka = 100.0
    for lahi, vari in ((0.1, KOROSTUS), (1.0, SININEN)):
        d = np.logspace(math.log10(lahi), 2, 300)
        z = ((kauka + lahi) / (lahi - kauka) * -d
             + 2 * kauka * lahi / (lahi - kauka)) / d
        ax.semilogx(d, z, color=vari, linewidth=1.3,
                    label=f"lähitaso {lahi:g}".replace(".", ","))
    ax.set(xlabel="etäisyys kamerasta", ylabel="syvyysarvo",
           ylim=(-1.05, 1.05))
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    for nimi, piirra in (("vektorit", vektorit), ("kuvaukset", kuvaukset),
                         ("jarjestys", jarjestys), ("suorat", suorat),
                         ("ehtoluku", ehtoluku),
                         ("determinantti", determinantti),
                         ("kannanvaihto", kannanvaihto),
                         ("sovitus", sovitus), ("ylisovitus", ylisovitus),
                         ("ominaisvektorit", ominaisvektorit),
                         ("potenssi", potenssi), ("pca", pca), ("svd", svd),
                         ("matala-aste", matala_aste),
                         ("keskipiste", keskipiste), ("syvyys", syvyys)):
        piirra(kohde / f"{nimi}.png")


if __name__ == "__main__":
    main()
