"""Piirtää selittävät piirrokset ja mittaustulosten kuvaajat.
Käyttö: make kuvat

Renderöidyt kuvat tulevat esimerkkiohjelmista (ks. Makefile). Tämä
skripti tekee geometriset periaatekuvat ja kuvaajat, joiden luvut
luetaan esimerkkien testatuista tulosteista (esimerkit/*.odotettu).
Kuvat ovat versionhallinnassa, joten skriptiä ei ajeta testeissä.
"""

from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle

KOROSTUS = "#4552B0"
TOINEN = "#C0652A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}
JUURI = Path(__file__).resolve().parent.parent


def uusi(leveys: float, korkeus: float) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def tallenna(fig: Figure, nimi: str) -> None:
    fig.savefig(JUURI / "kuvat" / nimi, metadata=METATIEDOT)


def nuoli(ax, a, b, vari=HARMAA, leveys=1.2, tyyli="-|>") -> None:
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=tyyli, mutation_scale=9,
                                 color=vari, linewidth=leveys,
                                 shrinkA=0, shrinkB=0))


def yks(aste: float) -> np.ndarray:
    return np.array([np.cos(np.radians(aste)), np.sin(np.radians(aste))])


def taulukko(nimi: str, ohita: int) -> np.ndarray:
    """Lukee esimerkin testatun tulosteen lukutaulukon."""
    rivit = (JUURI / "esimerkit" / nimi).read_text().splitlines()[ohita:]
    return np.array([[float(x) for x in r.replace("/", " ").split()]
                     for r in rivit if r.strip()])


def kamera() -> None:
    """Neulanreikäkamera sivulta: silmä, kuvataso ja pikselin säde."""
    fig = uusi(4.6, 2.2)
    ax = fig.add_subplot()
    f = 1.5
    ax.plot([f, f], [-1, 1], color=KOROSTUS, linewidth=1.6)
    for y in np.linspace(-1, 1, 9):
        ax.plot([f - 0.05, f + 0.05], [y, y], color=KOROSTUS, linewidth=0.8)
    ax.plot(0, 0, "o", color="black", markersize=4)
    ax.add_patch(Circle((4.6, 0.75), 0.6, facecolor=VAALEA,
                        edgecolor=HARMAA, linewidth=0.8))
    kohde = np.array([4.08, 0.45])
    pikseli = kohde * f / kohde[0]
    ax.plot([0, pikseli[0]], [0, pikseli[1]], color=TOINEN, linewidth=1.2)
    nuoli(ax, tuple(pikseli), tuple(kohde), TOINEN)
    ax.plot(*pikseli, "s", color=TOINEN, markersize=4)
    ax.plot(*kohde, "o", color=TOINEN, markersize=3.5)
    ax.plot([0, 5.6], [0, 0], color=HARMAA, linewidth=0.6, linestyle=":")
    ax.annotate("", (f, -1.22), (0, -1.22),
                arrowprops={"arrowstyle": "<->", "color": HARMAA,
                            "linewidth": 0.7})
    ax.text(f / 2, -1.42, "$f$", ha="center", color=HARMAA)
    ax.annotate("", (f + 0.28, 1), (f + 0.28, -1),
                arrowprops={"arrowstyle": "<->", "color": HARMAA,
                            "linewidth": 0.7})
    ax.text(f + 0.36, -0.55, "2", color=HARMAA)
    ax.add_patch(Arc((0, 0), 1.3, 1.3, theta1=-33.7, theta2=33.7,
                     color=HARMAA, linewidth=0.8))
    ax.text(0.72, -0.2, "$\\theta$", color=HARMAA)
    ax.text(-0.1, 0.25, "silmä $\\mathbf{o}$", ha="center", fontsize=8)
    ax.text(f, 1.12, "kuvataso", ha="center", color=KOROSTUS, fontsize=8)
    ax.text(pikseli[0] - 0.12, pikseli[1] + 0.2, "pikseli", color=TOINEN,
            fontsize=8, ha="right")
    ax.text(2.6, 0.52, "$\\mathbf{o} + t\\,\\mathbf{d}$", color=TOINEN,
            fontsize=9)
    ax.text(kohde[0] - 0.25, kohde[1] - 0.42, "lähin osuma", color=TOINEN,
            fontsize=8, ha="right")
    ax.set(xlim=(-0.7, 5.5), ylim=(-1.6, 1.5), aspect="equal")
    ax.axis("off")
    tallenna(fig, "02-kamerakaavio.png")


def leikkaukset() -> None:
    """Säde ja pallo (kaksi juurta) sekä laattamenetelmän välit."""
    fig = uusi(3.2, 2.2)
    ax = fig.add_subplot()
    c, r = np.array([3.0, 0.9]), 1.1
    o, d = np.array([0.0, 0.0]), yks(12)
    ax.add_patch(Circle(tuple(c), r, facecolor=KOROSTUS, alpha=0.12,
                        edgecolor=KOROSTUS, linewidth=1.1))
    b = np.dot(c - o, d)
    lahin = o + b * d
    q = np.sqrt(r * r - np.dot(c - lahin, c - lahin))
    t1, t2 = b - q, b + q
    nuoli(ax, tuple(o), tuple(o + 5.2 * d), TOINEN)
    for t, nimi in ((t1, "$t_1$"), (t2, "$t_2$")):
        p = o + t * d
        ax.plot(*p, "o", color=TOINEN, markersize=4)
        ax.text(p[0] - 0.05, p[1] - 0.38, nimi, color=TOINEN, ha="center")
    ax.plot(*c, "o", color=KOROSTUS, markersize=3)
    ax.plot([c[0], lahin[0]], [c[1], lahin[1]], color=HARMAA, linewidth=0.8,
            linestyle="--")
    ax.text(c[0] + 0.12, c[1] + 0.12, "$\\mathbf{c}$", color=KOROSTUS)
    ax.text((c[0] + lahin[0]) / 2 - 0.3, (c[1] + lahin[1]) / 2 - 0.02,
            "$\\mathbf{l}$", color=HARMAA)
    ax.plot(*o, "o", color="black", markersize=3.5)
    ax.text(-0.05, 0.22, "$\\mathbf{o}$")
    ax.text(4.9, 0.72, "$\\mathbf{d}$", color=TOINEN)
    sis = c + np.array([0.35, 0.45])
    nuoli(ax, tuple(sis), tuple(sis + 1.5 * yks(35)), HARMAA, 0.9)
    ax.plot(*sis, "o", color=HARMAA, markersize=3)
    ax.text(sis[0] + 0.2, sis[1] + 1.0, "sisältä alkava säde:\nvain $t_2 > 0$",
            fontsize=7, color=HARMAA, ha="center")
    ax.set(xlim=(-0.4, 5.6), ylim=(-0.5, 3.0), aspect="equal")
    ax.axis("off")
    tallenna(fig, "03-pallo.png")
    fig = uusi(3.4, 1.9)
    ax = fig.add_subplot()
    x0, x1, y0, y1 = 2.0, 4.4, 0.5, 1.9
    ax.axvspan(x0, x1, color=KOROSTUS, alpha=0.08, linewidth=0)
    ax.axhspan(y0, y1, color=TOINEN, alpha=0.08, linewidth=0)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                           edgecolor="black", linewidth=1.1))
    o, d = np.array([0.3, 0.1]), yks(21)
    nuoli(ax, tuple(o), tuple(o + 5.6 * d), HARMAA, 0.9)
    tx = sorted(((x0 - o[0]) / d[0], (x1 - o[0]) / d[0]))
    ty = sorted(((y0 - o[1]) / d[1], (y1 - o[1]) / d[1]))
    siirto = np.array([-d[1], d[0]])
    for (a, b_), vari, s, nimi in ((tx, KOROSTUS, 0.2, "x-laatan väli"),
                                   (ty, TOINEN, 0.4, "y-laatan väli")):
        p, q_ = o + a * d + s * siirto, o + b_ * d + s * siirto
        ax.plot([p[0], q_[0]], [p[1], q_[1]], color=vari, linewidth=2.2,
                solid_capstyle="butt")
        ax.text(*(q_ + (np.array([0.12, -0.45]) if nimi[0] == "x"
                        else np.array([-0.5, 0.2]))), nimi, color=vari,
                fontsize=7)
    a, b_ = max(tx[0], ty[0]), min(tx[1], ty[1])
    p, q_ = o + a * d, o + b_ * d
    ax.plot([p[0], q_[0]], [p[1], q_[1]], color="black", linewidth=2.4,
            solid_capstyle="butt")
    ax.text(3.3, 0.9, "leikkaus", fontsize=7, rotation=21)
    ax.plot(*o, "o", color="black", markersize=3.5)
    ax.set(xlim=(0, 6.2), ylim=(-0.3, 2.9), aspect="equal")
    ax.axis("off")
    tallenna(fig, "03-laatta.png")


def bvh() -> None:
    """Kahdeksan kolmion BVH tasossa: sisäkkäiset laatikot ja puu.
    Puu rakennetaan keskikohtajaolla pisimmän akselin suhteen kuten
    luvun rakenna_bvh (lehdessä yksi kolmio)."""
    keskipisteet = np.array([[0.7, 0.8], [1.5, 2.2], [2.3, 0.9], [3.0, 2.6],
                             [5.0, 0.7], [5.6, 1.9], [6.8, 1.0], [7.3, 2.5]])
    kulmat = np.array([[-0.35, -0.25], [0.4, -0.2], [0.0, 0.4]])
    kolmiot = [kp + kulmat * (0.8 + 0.1 * (i % 3))
               for i, kp in enumerate(keskipisteet)]
    varit = [KOROSTUS, TOINEN, "#3E7F3C", HARMAA]
    solmut = []  # (syvyys, laatikko, lapset tai kolmion indeksi)

    def rakenna(idx, syvyys):
        pisteet = np.concatenate([kolmiot[i] for i in idx])
        lo, hi = pisteet.min(axis=0), pisteet.max(axis=0)
        oma = len(solmut)
        solmut.append([syvyys, (lo, hi), None, idx])
        if len(idx) > 1:
            akseli = int(np.argmax(hi - lo))
            keski = (lo[akseli] + hi[akseli]) / 2
            vasen = [i for i in idx if keskipisteet[i][akseli] < keski]
            oikea = [i for i in idx if keskipisteet[i][akseli] >= keski]
            solmut[oma][2] = (rakenna(vasen, syvyys + 1),
                              rakenna(oikea, syvyys + 1))
        return oma

    rakenna(list(range(8)), 0)
    fig = uusi(5.6, 2.3)
    ax = fig.add_subplot(1, 2, 1)
    for syvyys, (lo, hi), lapset, _ in solmut:
        if lapset is None:
            continue
        vara = 0.22 - 0.07 * syvyys
        ax.add_patch(Rectangle(tuple(lo - vara), *(hi - lo + 2 * vara),
                               fill=False, edgecolor=varit[syvyys],
                               linewidth=1.5 - 0.3 * syvyys))
    for i, t in enumerate(kolmiot):
        ax.add_patch(Polygon(t, facecolor=VAALEA, edgecolor=HARMAA,
                             linewidth=0.6))
        ax.text(*keskipisteet[i], str(i), fontsize=6, ha="center",
                va="center")
    ax.set(xlim=(-0.2, 8.2), ylim=(0.1, 3.4), aspect="equal")
    ax.axis("off")
    # puu: lehdet tasavälein vasemmalta oikealle
    ax = fig.add_subplot(1, 2, 2)
    paikat = {}
    seuraava = [0]

    def sijoita(i):
        syvyys, _, lapset, idx = solmut[i]
        if lapset is None:
            x = seuraava[0]
            seuraava[0] += 1
        else:
            x = (sijoita(lapset[0]) + sijoita(lapset[1])) / 2
        paikat[i] = (x, -syvyys)
        return x

    sijoita(0)
    for i, (syvyys, _, lapset, idx) in enumerate(solmut):
        x, y = paikat[i]
        if lapset is not None:
            for lapsi in lapset:
                ax.plot([x, paikat[lapsi][0]], [y, paikat[lapsi][1]],
                        color=HARMAA, linewidth=0.7, zorder=1)
            ax.add_patch(Rectangle((x - 0.32, y - 0.2), 0.64, 0.4,
                                   facecolor="white",
                                   edgecolor=varit[syvyys],
                                   linewidth=1.5 - 0.3 * syvyys, zorder=2))
        else:
            ax.add_patch(Polygon([(x - 0.25, y - 0.18), (x + 0.25, y - 0.18),
                                  (x, y + 0.22)], facecolor=VAALEA,
                                 edgecolor=HARMAA, linewidth=0.6, zorder=2))
            ax.text(x, y - 0.05, str(idx[0]), fontsize=6, ha="center",
                    va="center", zorder=3)
    ax.set(xlim=(-0.6, 7.6), ylim=(-3.5, 0.5))
    ax.axis("off")
    tallenna(fig, "04-bvh-periaate.png")


def snell() -> None:
    """Taittuminen ilmasta lasiin ja kokonaisheijastus lasista ilmaan."""
    fig = uusi(5.2, 2.3)
    n_lasi = 1.5
    for i, (otsikko, tulo, ylla, alla) in enumerate((
            ("ilmasta lasiin", 50.0, "ilma $n_1 = 1{,}0$",
             "lasi $n_2 = 1{,}5$"),
            ("lasista ilmaan, yli kriittisen kulman", 55.0,
             "lasi $n_1 = 1{,}5$", "ilma $n_2 = 1{,}0$"))):
        ax = fig.add_subplot(1, 2, i + 1)
        (ax.axhspan(-1.6, 0, color=KOROSTUS, alpha=0.12, linewidth=0)
         if i == 0 else
         ax.axhspan(0, 1.6, color=KOROSTUS, alpha=0.12, linewidth=0))
        ax.axhline(0, color="black", linewidth=1)
        ax.plot([0, 0], [-1.5, 1.5], color=HARMAA, linewidth=0.6,
                linestyle=":")
        nuoli(ax, (0, 0), (0, 1.05), "black", 0.9)
        ax.text(0.08, 1.0, "$\\mathbf{n}$")
        a = np.radians(tulo)
        tuleva = 1.5 * np.array([-np.sin(a), np.cos(a)])
        nuoli(ax, tuple(tuleva), (0, 0), TOINEN)
        heij = 1.5 * np.array([np.sin(a), np.cos(a)])
        eta = 1 / n_lasi if i == 0 else n_lasi
        s2 = eta * np.sin(a)
        if s2 < 1:
            b = np.arcsin(s2)
            nuoli(ax, (0, 0), tuple(1.5 * np.array([np.sin(b), -np.cos(b)])),
                  TOINEN)
            nuoli(ax, (0, 0), tuple(0.9 * heij / 1.5), HARMAA, 0.8)
            ax.add_patch(Arc((0, 0), 1.2, 1.2, theta1=270,
                             theta2=270 + np.degrees(b), color=TOINEN,
                             linewidth=0.8))
            ax.text(0.12, -0.92, "$\\theta_2$", color=TOINEN)
            ax.text(0.95, 0.5, "heijastunut\nosuus $F$", fontsize=7,
                    color=HARMAA)
            ax.text(0.75, -1.25, "taittunut\n$1 - F$", fontsize=7,
                    color=TOINEN)
        else:
            nuoli(ax, (0, 0), tuple(heij), TOINEN)
            ax.text(0.5, -0.5, "ei taittunutta\nsädettä", fontsize=7,
                    color=HARMAA)
        ax.add_patch(Arc((0, 0), 1.2, 1.2, theta1=90, theta2=90 + tulo,
                         color=TOINEN, linewidth=0.8))
        ax.text(-0.42, 0.72, "$\\theta_1$", color=TOINEN)
        ax.text(-1.95, 1.3, ylla, fontsize=7)
        ax.text(-1.95, -1.45, alla, fontsize=7)
        ax.set(xlim=(-2, 2), ylim=(-1.6, 1.6), aspect="equal")
        ax.set_title(otsikko, fontsize=8)
        ax.axis("off")
    tallenna(fig, "05-snell.png")


def fresnel() -> None:
    """Heijastuskerroin tulokulman funktiona esimerkin 05-fresnel
    testatusta tulosteesta."""
    t = taulukko("05-fresnel.odotettu", 2)
    kulma = np.degrees(np.arccos(t[:, 0]))
    fig = uusi(4.4, 2.6)
    ax = fig.add_subplot()
    ax.plot(kulma, t[:, 1], "o-", color=KOROSTUS, markersize=3,
            linewidth=1.2, label="ilma → lasi, tarkka")
    ax.plot(kulma, t[:, 2], "s--", color=KOROSTUS, markersize=3,
            linewidth=0.9, alpha=0.6, label="ilma → lasi, Schlick")
    ax.plot(kulma, t[:, 3], "o-", color=TOINEN, markersize=3,
            linewidth=1.2, label="lasi → ilma, tarkka")
    ax.plot(kulma, t[:, 4], "s--", color=TOINEN, markersize=3,
            linewidth=0.9, alpha=0.6, label="lasi → ilma, Schlick")
    ax.axvline(np.degrees(np.arcsin(1 / 1.5)), color=HARMAA, linewidth=0.6,
               linestyle=":")
    ax.text(43, 0.5, "kriittinen\nkulma", fontsize=7, color=HARMAA)
    ax.set(xlabel="tulokulma (astetta normaalista)",
           ylabel="heijastuskerroin F", xlim=(0, 90), ylim=(0, 1.03))
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    tallenna(fig, "05-fresnel.png")


def puolipallo() -> None:
    """Pallonpuolisko pinnan pisteessä: tuleva ja lähtevä suunta."""
    fig = uusi(3.8, 2.2)
    ax = fig.add_subplot()
    ax.plot([-2.2, 2.2], [0, 0], color="black", linewidth=1.3)
    ax.fill_between([-2.2, 2.2], -0.2, 0, color=VAALEA, alpha=0.5,
                    linewidth=0)
    ax.add_patch(Arc((0, 0), 3.6, 3.6, theta1=0, theta2=180, color=HARMAA,
                     linewidth=0.7, linestyle=":"))
    nuoli(ax, (0, 0), (0, 1.8), "black", 0.9)
    ax.text(0.08, 1.85, "$\\mathbf{n}$")
    wi, wo = yks(125), yks(40)
    kartio = [(0, 0)] + [tuple(1.8 * yks(a)) for a in np.linspace(118, 132, 8)]
    ax.add_patch(Polygon(kartio, facecolor=TOINEN, alpha=0.25,
                         edgecolor="none"))
    nuoli(ax, tuple(1.8 * wi), (0, 0), TOINEN)
    nuoli(ax, (0, 0), tuple(1.8 * wo), KOROSTUS)
    ax.text(*(2.0 * wi + np.array([-0.25, 0.05])), "$\\omega_i$",
            color=TOINEN, fontsize=11)
    ax.text(*(2.0 * wo), "$\\omega_o$", color=KOROSTUS, fontsize=11)
    ax.text(-1.55, 1.05, "$d\\omega_i$", color=TOINEN, fontsize=8)
    ax.add_patch(Arc((0, 0), 1.3, 1.3, theta1=90, theta2=125, color=TOINEN,
                     linewidth=0.8))
    ax.text(-0.32, 0.75, "$\\theta_i$", color=TOINEN, fontsize=9)
    ax.text(-2.1, 0.5, "$L_i(\\omega_i)$", color=TOINEN, fontsize=8)
    ax.text(1.45, 0.62, "$L_o(\\omega_o)$", color=KOROSTUS, fontsize=8)
    ax.text(1.0, -0.42, "pinta-ala $dA$", fontsize=7, color=HARMAA,
            ha="center")
    ax.set(xlim=(-2.4, 2.4), ylim=(-0.5, 2.2), aspect="equal")
    ax.axis("off")
    tallenna(fig, "06-puolipallo.png")


def konvergenssi() -> None:
    """Estimaattorien virhe ja harha näytemäärän funktiona esimerkin
    07-montecarlo testatusta tulosteesta."""
    rivit = (JUURI / "esimerkit" / "07-montecarlo.odotettu").read_text()
    tarkka = float(rivit.splitlines()[0].split("=")[1])
    t = taulukko("07-montecarlo.odotettu", 2)
    n = t[:, 0]
    fig = uusi(5.4, 2.5)
    ax = fig.add_subplot(1, 2, 1)
    ax.loglog(n, t[:, 1], "o-", color=HARMAA, markersize=3.5,
              label="tasainen poiminta")
    ax.loglog(n, t[:, 2], "o-", color=KOROSTUS, markersize=3.5,
              label="kosinipainotettu")
    ax.loglog(n, 5.6 / np.sqrt(n) * 1.8, color=VAALEA, linewidth=0.9,
              linestyle="--")
    ax.text(40, 2.0, "$\\propto 1/\\sqrt{N}$", fontsize=8, color=HARMAA)
    ax.set(xlabel="näytteitä N", ylabel="RMSE")
    ax.set_xticks(n, [str(int(x)) for x in n])
    ax.minorticks_off()
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ax = fig.add_subplot(1, 2, 2)
    ax.semilogx(n, t[:, 5], "s-", color=TOINEN, markersize=3.5,
                label="väärä tiheys: keskiarvo")
    ax.axhline(tarkka, color="black", linewidth=0.9)
    ax.text(5, tarkka + 0.15, f"tarkka arvo {tarkka:.2f}".replace(".", ","),
            fontsize=7)
    ax.set(xlabel="näytteitä N", ylabel="estimaatti E", ylim=(6.5, 11.2))
    ax.set_xticks(n, [str(int(x)) for x in n])
    ax.minorticks_off()
    ax.legend(frameon=False, fontsize=7, loc="center right")
    tallenna(fig, "07-konvergenssi.png")


def mikrofasetit() -> None:
    """Mikrofasetit: vain fasetit, joiden normaali on h, heijastavat
    valon katsojalle; osa on varjossa tai peitossa."""
    fig = uusi(4.6, 2.1)
    ax = fig.add_subplot()
    l_, v = yks(110), yks(20)
    h = (l_ + v) / np.linalg.norm(l_ + v)
    kulma_h = np.degrees(np.arctan2(h[1], h[0]))
    # sahalaitainen pinta: fasettien kaltevuudet käsin valittu
    kaltevuudet = [30, kulma_h - 90, 40, -50, 35, kulma_h - 90, 45, -40,
                   25, -20]
    x, y, pisteet = 0.0, 0.0, [(0.0, 0.0)]
    for k in kaltevuudet:
        pituus = 0.55
        x += pituus * np.cos(np.radians(k))
        y += pituus * np.sin(np.radians(k))
        pisteet.append((x, y))
    p = np.array(pisteet)
    p[:, 1] -= np.linspace(p[0, 1], p[-1, 1], len(p))  # suorista keskitaso
    p[:, 0] -= p[:, 0].mean()
    ax.fill_between(p[:, 0], p[:, 1], -0.7, color=VAALEA, alpha=0.6,
                    linewidth=0)
    ax.plot(p[:, 0], p[:, 1], color="black", linewidth=1)
    for i, k in enumerate(kaltevuudet):
        if abs(k - (kulma_h - 90)) < 1e-9:
            a, b = p[i], p[i + 1]
            ax.plot([a[0], b[0]], [a[1], b[1]], color=TOINEN, linewidth=2.6)
            m = (a + b) / 2
            suunta = np.array([-(b - a)[1], (b - a)[0]])
            suunta /= np.linalg.norm(suunta)
            nuoli(ax, tuple(m), tuple(m + 0.55 * suunta), TOINEN, 0.9)
    keski = np.array([0.0, 1.0])
    for vek, nimi, vari in ((np.array([0.0, 1.0]), "n", "black"),
                            (l_, "l", HARMAA), (v, "v", KOROSTUS),
                            (h, "h", TOINEN)):
        nuoli(ax, tuple(keski), tuple(keski + 0.95 * vek), vari, 1.0)
        ax.text(*(keski + 1.12 * vek), f"$\\mathbf{{{nimi}}}$", color=vari,
                ha="center", va="center", fontsize=10)
    ax.text(2.35, 0.75, "fasetit, joiden\nnormaali on $\\mathbf{h}$",
            fontsize=7, color=TOINEN, ha="center")
    ax.text(-1.3, 2.0, "valoon", fontsize=7, color=HARMAA)
    ax.text(1.25, 1.2, "katsojaan", fontsize=7, color=KOROSTUS)
    ax.text(0, -0.55, "makropinta, normaali $\\mathbf{n}$", fontsize=7,
            ha="center")
    ax.set(xlim=(-3.0, 3.0), ylim=(-0.7, 2.3), aspect="equal")
    ax.axis("off")
    tallenna(fig, "09-mikrofasetit.png")


def naytepisteet() -> None:
    """Satunnaiset, ositetut ja Haltonin pisteet sekä integroinnin virhe
    (esimerkin 10-naytteistys testattu tuloste). Satunnaiset ja ositetut
    pisteet ovat periaatekuva (NumPyn generaattori, kiinteä siemen)."""
    def kaanteinen(i: int, kanta: int) -> float:
        tulos, osa = 0.0, 1.0 / kanta
        while i > 0:
            tulos += (i % kanta) * osa
            i //= kanta
            osa /= kanta
        return tulos

    g = np.random.default_rng(2026)
    n, m = 64, 8
    satunnaiset = g.random((n, 2))
    ruudut = np.array([[i, j] for j in range(m) for i in range(m)])
    ositetut = (ruudut + g.random((n, 2))) / m
    halton = np.array([[kaanteinen(i, 2), kaanteinen(i, 3)]
                       for i in range(1, n + 1)])
    fig = uusi(5.6, 4.0)
    ruudukko = fig.add_gridspec(2, 3, height_ratios=[1, 1.15])
    for i, (nimi, pisteet) in enumerate((("satunnaiset", satunnaiset),
                                         ("ositetut", ositetut),
                                         ("Halton (2, 3)", halton))):
        ax = fig.add_subplot(ruudukko[0, i])
        if i == 1:
            for k in range(1, m):
                ax.plot([k / m, k / m], [0, 1], color=VAALEA, linewidth=0.3)
                ax.plot([0, 1], [k / m, k / m], color=VAALEA, linewidth=0.3)
        ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, edgecolor="black",
                               linewidth=0.8))
        ax.plot(pisteet[:, 0], pisteet[:, 1], "o", color=KOROSTUS,
                markersize=2.2)
        ax.set(xlim=(-0.02, 1.02), ylim=(-0.02, 1.02), aspect="equal")
        ax.set_title(f"{nimi}, {n} pistettä", fontsize=8)
        ax.axis("off")
    t = taulukko("10-naytteistys.odotettu", 2)
    ax = fig.add_subplot(ruudukko[1, :])
    for sarake, nimi, vari in ((1, "satunnaiset", HARMAA),
                               (2, "ositetut", KOROSTUS),
                               (3, "Halton", TOINEN)):
        ax.loglog(t[:, 0], t[:, sarake], "o-", color=vari, markersize=3.5,
                  label=nimi)
    ax.loglog(t[:, 0], 0.7 / np.sqrt(t[:, 0]), color=VAALEA, linewidth=0.9,
              linestyle="--")
    ax.loglog(t[:, 0], 0.25 * t[:, 0] ** -0.75, color=VAALEA, linewidth=0.9,
              linestyle=":")
    ax.text(300, 0.047, "$N^{-1/2}$", fontsize=8, color=HARMAA)
    ax.text(300, 0.0018, "$N^{-3/4}$", fontsize=8, color=HARMAA)
    ax.set(xlabel="näytteitä N", ylabel="RMSE")
    ax.set_xticks(t[:, 0], [str(int(x)) for x in t[:, 0]])
    ax.minorticks_off()
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    tallenna(fig, "10-naytepisteet.png")


if __name__ == "__main__":
    kamera()
    leikkaukset()
    bvh()
    snell()
    fresnel()
    puolipallo()
    konvergenssi()
    mikrofasetit()
    naytepisteet()
