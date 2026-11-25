"""Piirtää selittävät piirrokset ja kuvaajat. Käyttö: make kuvat

Renderöidyt kuvat tulevat esimerkkiohjelmista (ks. Makefile); tämä
skripti tekee geometriset periaatekuvat ja syvyyden jakauman kuvaajan.
Kuvat ovat versionhallinnassa, joten skriptiä ei ajeta testeissä.
Näytekuvio ja kolmion kärjet luetaan esimerkkien lähdekoodista, jotta
kuva vastaa koodia.
"""

import re
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import Arc, FancyArrowPatch, Polygon, Rectangle

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


def nuoli(ax, a, b, vari=HARMAA, leveys=1.2) -> None:
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9,
                                 color=vari, linewidth=leveys,
                                 shrinkA=0, shrinkB=0))


def reunafunktio() -> None:
    """Kolmio pikseliruudukolla: keskipisteiden testi ja rajaava
    suorakulmio. Sama sääntö kuin rasteroijassa (ilman kiinteää pilkkua)."""
    a, b, c = (1.6, 1.3), (3.2, 8.4), (11.5, 5.6)  # vastapäivään ruudulla
    fig = uusi(4.4, 3.2)
    ax = fig.add_subplot()
    L, K = 13, 10

    def reuna(p, q, r):
        return (r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])

    for x in range(L + 1):
        ax.plot([x, x], [0, K], color=VAALEA, linewidth=0.4)
    for y in range(K + 1):
        ax.plot([0, L], [y, y], color=VAALEA, linewidth=0.4)
    x0, x1 = int(min(a[0], b[0], c[0])), int(max(a[0], b[0], c[0]))
    y0, y1 = int(min(a[1], b[1], c[1])), int(max(a[1], b[1], c[1]))
    ax.add_patch(Rectangle((x0, y0), x1 - x0 + 1, y1 - y0 + 1, fill=False,
                           edgecolor=TOINEN, linewidth=1, linestyle="--"))
    ala = reuna(a, b, c)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            p = (x + 0.5, y + 0.5)
            w = [reuna(b, c, p) / ala, reuna(c, a, p) / ala,
                 reuna(a, b, p) / ala]
            sisalla = min(w) >= 0
            if sisalla:
                ax.add_patch(Rectangle((x, y), 1, 1, color=KOROSTUS,
                                       alpha=0.25, linewidth=0))
            ax.plot(*p, "o", markersize=2.2,
                    color=KOROSTUS if sisalla else VAALEA)
    ax.add_patch(Polygon([a, b, c], fill=False, edgecolor="black",
                         linewidth=1.1))
    for nimi, p, siirto in (("a", a, (-0.5, -0.3)), ("b", b, (-0.4, 0.5)),
                            ("c", c, (0.3, 0.2))):
        ax.text(p[0] + siirto[0], p[1] + siirto[1], nimi, fontsize=10,
                ha="center", va="center", style="italic")
    ax.text(5.2, 5.2, "kaikki $E \\geq 0$", color=KOROSTUS, fontsize=8)
    ax.text(8.6, 2.6, "$E_{ca} < 0$", color=HARMAA, fontsize=8)
    ax.text(9.2, 8.6, "$E_{bc} < 0$", color=HARMAA, fontsize=8)
    ax.text(0.15, 5.4, "$E_{ab} < 0$", color=HARMAA, fontsize=8,
            rotation=78)
    ax.text(x1 + 0.9, y1 + 1.15, "rajaava suorakulmio", color=TOINEN,
            fontsize=7, va="top", ha="right")
    ax.set(xlim=(0, L), ylim=(K, 0), aspect="equal", xlabel="x",
           ylabel="y (alas)")
    ax.set_xticks(range(0, L + 1, 2))
    ax.set_yticks(range(0, K + 1, 2))
    tallenna(fig, "04-reunafunktio.png")


def nakymakartio() -> None:
    """Näkymäkartio sivulta: silmä, lähi- ja kaukotaso, näkökenttä."""
    fig = uusi(4.6, 2.3)
    ax = fig.add_subplot()
    lahi, kauka, puolikulma = 2.0, 6.4, np.radians(28)
    t = np.tan(puolikulma)
    ax.add_patch(Polygon([(lahi, -lahi * t), (lahi, lahi * t),
                          (kauka, kauka * t), (kauka, -kauka * t)],
                         facecolor=KOROSTUS, alpha=0.15, edgecolor="none"))
    for s in (1, -1):
        ax.plot([0, kauka + 0.6], [0, s * (kauka + 0.6) * t], color=HARMAA,
                linewidth=0.7, linestyle=":")
    ax.plot([lahi, lahi], [-lahi * t, lahi * t], color=KOROSTUS,
            linewidth=1.6)
    ax.plot([kauka, kauka], [-kauka * t, kauka * t], color=KOROSTUS,
            linewidth=1.6)
    ax.plot(0, 0, "o", color="black", markersize=4)
    nuoli(ax, (0, 0), (3.4, 0), "black", 0.9)
    ax.text(-0.15, 0.28, "silmä", ha="center", fontsize=8)
    ax.text(3.5, 0.12, "katse ($-z$)", fontsize=8)
    ax.text(lahi, lahi * t + 0.15, "lähitaso", ha="center", va="bottom",
            fontsize=8, color=KOROSTUS)
    ax.text(kauka, -kauka * t - 0.28, "kaukotaso", ha="center", va="top",
            fontsize=8, color=KOROSTUS)
    ax.add_patch(Arc((0, 0), 1.9, 1.9, theta1=-28, theta2=28,
                     color=TOINEN, linewidth=1))
    ax.text(1.05, 0.2, "$\\theta$", color=TOINEN, fontsize=10)
    ax.text(4.3, 1.3, "näkyvä alue", color=KOROSTUS, fontsize=8)
    ax.plot([5.0], [-1.6], "s", color=TOINEN, markersize=5)
    ax.plot([0, 5.0], [0, -1.6], color=TOINEN, linewidth=0.6)
    ax.plot([lahi], [-1.6 * lahi / 5.0], "o", color=TOINEN, markersize=3)
    ax.text(5.15, -1.7, "piste", fontsize=7, color=TOINEN, va="top")
    ax.text(lahi + 0.15, -0.95, "pisteen kuva", fontsize=7,
            color=TOINEN, va="top")
    ax.set(xlim=(-0.7, kauka + 1.2), ylim=(-kauka * t - 0.9,
                                          kauka * t + 0.3), aspect="equal")
    ax.axis("off")
    tallenna(fig, "05-nakymakartio.png")


def leikkaus() -> None:
    """Sutherland–Hodgman: kolmio tasoa vastaan, yksi ja kaksi kärkeä
    tason takana."""
    fig = uusi(5.0, 2.2)
    tapaukset = (
        ("yksi kärki takana: nelikulmio",
         [(0.8, 2.6), (3.6, 2.9), (2.6, -1.0)]),
        ("kaksi kärkeä takana: kolmio",
         [(2.2, 2.8), (0.5, -0.9), (3.7, -1.3)]),
    )
    for i, (otsikko, kolmio) in enumerate(tapaukset):
        ax = fig.add_subplot(1, 2, i + 1)
        ax.axhspan(-1.8, 0, color=VAALEA, alpha=0.35, linewidth=0)
        ax.axhline(0, color="black", linewidth=1)
        ax.text(4.25, 0.08, "taso", fontsize=7, ha="right")
        ax.text(4.25, -1.7, "hylätty puoli ($d < 0$)", fontsize=7,
                ha="right", color=HARMAA)
        ax.add_patch(Polygon(kolmio, fill=False, edgecolor=HARMAA,
                             linewidth=0.8, linestyle="--"))
        tulos = []
        for j in range(3):  # sama silmukka kuin funktiossa leikkaa_lahitaso
            p, q = kolmio[j], kolmio[(j + 1) % 3]
            if p[1] >= 0:
                tulos.append((p, False))
            if (p[1] >= 0) != (q[1] >= 0):
                t = p[1] / (p[1] - q[1])
                tulos.append(((p[0] + t * (q[0] - p[0]), 0.0), True))
        ax.add_patch(Polygon([p for p, _ in tulos], facecolor=KOROSTUS,
                             alpha=0.22, edgecolor=KOROSTUS, linewidth=1.3))
        for p in kolmio:
            ax.plot(*p, "o", markersize=4,
                    color=KOROSTUS if p[1] >= 0 else VAALEA,
                    markeredgecolor=HARMAA, markeredgewidth=0.5)
        for p, uusi_karki in tulos:
            if uusi_karki:
                ax.plot(*p, "s", markersize=4.5, color=TOINEN)
        ax.set(xlim=(0, 4.4), ylim=(-1.8, 3.3), aspect="equal")
        ax.set_title(otsikko, fontsize=8)
        ax.axis("off")
    tallenna(fig, "07-leikkaus-periaate.png")


def syvyysjakauma() -> None:
    """Syvyyspuskurin arvo etäisyyden funktiona kahdella lähitasolla.
    Sama kaava d = A - B / e kuin esimerkissä 08-syvyys.cpp."""
    fig = uusi(4.4, 2.6)
    ax = fig.add_subplot()
    kauka = 100.0
    for lahi, vari in ((0.1, KOROSTUS), (1.0, TOINEN)):
        e = np.logspace(np.log10(lahi), 2, 300)
        b = kauka * lahi / (kauka - lahi)
        a = kauka / (kauka - lahi)
        ax.semilogx(e, a - b / e, color=vari, linewidth=1.4,
                    label=f"lähitaso {lahi:g}".replace(".", ","))
    ax.axhline(0.5, color=HARMAA, linewidth=0.5, linestyle=":")
    ax.text(0.2, 0.52, "puolet arvoista käytetty", fontsize=7,
            color=HARMAA)
    ax.set(xlabel="etäisyys kamerasta (kaukotaso 100)",
           ylabel="syvyys d", ylim=(0, 1.02))
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    tallenna(fig, "08-syvyysjakauma.png")


def valaistusvektorit() -> None:
    """Vektorit n, l, v, r ja h pinnan pisteessä."""
    fig = uusi(4.0, 2.3)
    ax = fig.add_subplot()
    ax.plot([-2.6, 2.6], [0, 0], color="black", linewidth=1.4)
    ax.fill_between([-2.6, 2.6], -0.25, 0, color=VAALEA, alpha=0.5,
                    linewidth=0)

    def yks(aste):
        return np.array([np.cos(np.radians(aste)), np.sin(np.radians(aste))])

    n, l_, v = yks(90), yks(140), yks(25)
    r = 2 * np.dot(n, l_) * n - l_
    h = (l_ + v) / np.linalg.norm(l_ + v)
    pituus = 1.9
    for vek, nimi, vari in ((n, "n", "black"), (l_, "l", TOINEN),
                            (v, "v", KOROSTUS), (r, "r", HARMAA),
                            (h, "h", HARMAA)):
        nuoli(ax, (0, 0), tuple(pituus * vek), vari,
              1.3 if nimi in "nlv" else 0.9)
        ax.text(*(pituus * 1.1 * vek), f"${nimi}$", color=vari, fontsize=11,
                ha="center", va="center")
    ax.plot(*(2.45 * l_), marker="*", color=TOINEN, markersize=11)
    ax.text(*(2.45 * l_ + np.array([-0.15, 0.25])), "valo", fontsize=8,
            color=TOINEN, ha="center")
    ax.text(*(2.5 * v + np.array([0.1, 0.05])), "katsoja", fontsize=8,
            color=KOROSTUS)
    ax.add_patch(Arc((0, 0), 1.3, 1.3, theta1=90, theta2=140, color=TOINEN,
                     linewidth=0.8))
    ax.add_patch(Arc((0, 0), 1.3, 1.3, theta1=40, theta2=90, color=HARMAA,
                     linewidth=0.8))
    ax.text(-0.33, 0.78, "$\\theta$", fontsize=8, color=TOINEN)
    ax.text(0.2, 0.78, "$\\theta$", fontsize=8, color=HARMAA)
    ax.set(xlim=(-2.7, 3.2), ylim=(-0.3, 2.4), aspect="equal")
    ax.axis("off")
    tallenna(fig, "09-vektorit.png")


def naytekuviot() -> None:
    """Näytteiden paikat pikselin sisällä ja vaakasuoran reunan
    kirkkaustasot. Kierretty kuvio luetaan esimerkin lähdekoodista."""
    lahde = (JUURI / "esimerkit" / "11-antialiasointi.cpp").read_text()
    lohko = re.search(r"KIERRETTY = \{(.*?)\};", lahde, re.S)
    assert lohko, "kierrettyä kuviota ei löytynyt esimerkistä"
    kierretty = [(float(x), float(y)) for x, y in
                 re.findall(r"\{([\d.]+), ([\d.]+)\}", lohko.group(1))]
    assert len(kierretty) == 4

    def ruudukko(n):
        return [((i + 0.5) / n, (j + 0.5) / n) for j in range(n)
                for i in range(n)]

    fig = uusi(5.0, 2.0)
    for i, (nimi, pisteet) in enumerate((("2 × 2 -ruudukko", ruudukko(2)),
                                         ("4 × 4 -ruudukko", ruudukko(4)),
                                         ("4 kierrettyä", kierretty))):
        ax = fig.add_subplot(1, 3, i + 1)
        ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, edgecolor="black",
                               linewidth=1))
        rivit = sorted({y for _, y in pisteet})
        for y in rivit:
            ax.plot([0, 1.12], [y, y], color=VAALEA, linewidth=0.5)
            ax.plot([1.12], [y], marker="_", color=TOINEN, markersize=6)
        ax.plot([x for x, _ in pisteet], [y for _, y in pisteet], "o",
                color=KOROSTUS, markersize=4.5)
        ax.set(xlim=(-0.08, 1.25), ylim=(1.08, -0.08), aspect="equal")
        ax.set_title(f"{nimi}\n{len(pisteet)} näytettä, "
                     f"{len(rivit) + 1} tasoa", fontsize=8)
        ax.axis("off")
    tallenna(fig, "11-naytekuviot.png")


if __name__ == "__main__":
    reunafunktio()
    nakymakartio()
    leikkaus()
    syvyysjakauma()
    valaistusvektorit()
    naytekuviot()
