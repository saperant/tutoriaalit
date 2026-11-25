"""Piirtää paketin kuvat esimerkkiohjelmien tulosteista.

Käyttö: python3 kuvat/piirra.py kuvat   (ajetaan komennolla `make kuvat`)

Skripti kääntää esimerkit väliaikaiseen hakemistoon ja ajaa ne. Data on
joko sama tuloste, jonka testit tarkistavat (.odotettu), tai esimerkin
"käyrätila" (argumentti k), joka tulostaa saman laskennan välivaiheet.
Ruutukaappaukset ovat esimerkkien itse tallentamia PPM-kuvia. Kuvat ovat
versionhallinnassa.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

KOROSTUS = "#B04848"
TOINEN = "#2F5F9A"
KOLMAS = "#B07A2A"
VIHREA = "#3E7D5A"
HARMAA = "#5B6B70"
VAALEA = "#D9E0E3"
TUMMA = "#2B3438"
FONTIT = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({"font.family": "Inter" if "Inter" in FONTIT
                     else "DejaVu Sans",
                     "font.size": 9, "figure.dpi": 100, "savefig.dpi": 200,
                     "savefig.bbox": "tight", "axes.spines.top": False,
                     "axes.spines.right": False})

JUURI = Path(__file__).resolve().parent.parent
ESIM = JUURI / "esimerkit"
KAANTAJA = shutil.which("g++-14") or "g++"


class Ajaja:
    """Kääntää esimerkin kerran ja ajaa sen työhakemistossa."""

    def __init__(self, tyo: Path) -> None:
        self.tyo = tyo
        self.valmiit: dict[str, Path] = {}

    def binaari(self, nimi: str) -> Path:
        if nimi not in self.valmiit:
            polku = ESIM / nimi
            lahteet = (sorted(polku.glob("*.cpp")) if polku.is_dir()
                       else [polku.with_suffix(".cpp")])
            tulos = self.tyo / nimi.replace("/", "_")
            subprocess.run([KAANTAJA, "-std=c++23", "-O1", f"-I{ESIM}",
                            *map(str, lahteet), "-o", str(tulos)],
                           check=True)
            self.valmiit[nimi] = tulos
        return self.valmiit[nimi]

    def aja(self, nimi: str, *argumentit: str, syote: str = "") -> str:
        return subprocess.run([str(self.binaari(nimi)), *argumentit],
                              input=syote, capture_output=True, text=True,
                              check=True, cwd=self.tyo).stdout


def odotettu(nimi: str) -> str:
    return (ESIM / f"{nimi}.odotettu").read_text("utf-8")


def lue_ppm(polku: Path) -> np.ndarray:
    data = polku.read_bytes()
    osat = data.split(maxsplit=4)
    w, h = int(osat[1]), int(osat[2])
    return np.frombuffer(osat[4][:w * h * 3], dtype=np.uint8).reshape(h, w, 3)


def tallenna(fig: plt.Figure, kohde: Path, nimi: str) -> None:
    fig.savefig(kohde / nimi)
    plt.close(fig)
    print("kirjoitettu", nimi)


# --- Luku 2: pelisilmukka -------------------------------------------------

def aika_askel(a: Ajaja, kohde: Path) -> None:
    rivit = [list(map(int, r.split()))
             for r in a.aja("02-kiintea", "k").splitlines()]
    askel = 1000.0 / 60.0
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(6.6, 3.3), sharex=True,
                                 height_ratios=[1.5, 1])
    t = 0.0
    edellinen = 0
    kertymat = [(0.0, 0.0)]
    for n, kesto_ns, askelia in rivit:
        kesto = kesto_ns / 1e6
        ax.add_patch(Rectangle((t, 1.1), kesto, 0.7, fc=VAALEA, ec=HARMAA,
                               lw=0.8))
        ax.text(t + kesto / 2, 1.45, f"{kesto:.0f}", ha="center",
                va="center", fontsize=7)
        t += kesto
        for i in range(edellinen, askelia):
            ax.add_patch(Rectangle((i * askel, 0.1), askel, 0.7,
                                   fc="#C9D8EA", ec=TOINEN, lw=0.8))
            ax.annotate("", (i * askel + askel / 2, 0.8), (t, 1.1),
                        arrowprops={"arrowstyle": "-|>", "color": KOROSTUS,
                                    "lw": 0.7})
        # Kertymä ruudun lopussa ennen askelia ja niiden jälkeen.
        kertymat.append((t, t - edellinen * askel))
        kertymat.append((t, t - askelia * askel))
        edellinen = askelia
    ax.set_ylim(0, 1.9)
    ax.set_yticks([0.45, 1.45], ["simulaation\naskeleet (16,7 ms)",
                                 "ruudut (ms)"])
    ax.tick_params(left=False)
    ax.spines["left"].set_visible(False)
    bx.plot(*zip(*kertymat), color=TOINEN, lw=1.2)
    bx.axhline(askel, color=KOROSTUS, lw=0.8, ls="--")
    bx.text(1.0, askel + 1.0, "askel 16,7 ms", ha="left", color=KOROSTUS,
            fontsize=7)
    bx.set_ylabel("kertymä (ms)")
    bx.set_xlabel("seinäkellon aika (ms)")
    bx.set_ylim(0, 38)
    bx.set_xlim(0, t + 2)
    tallenna(fig, kohde, "aika-askel.png")


def interpolointi(a: Ajaja, kohde: Path) -> None:
    rivit = [r.split() for r in a.aja("02-interpolointi", "k").splitlines()[1:]]
    ruutu = [int(r[0]) for r in rivit]
    ilman = [float(r[1]) for r in rivit]
    interp = [float(r[2]) for r in rivit]
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    ax.step(ruutu, ilman, where="post", color=KOROSTUS, lw=1.0, alpha=0.5)
    ax.plot(ruutu, ilman, "o", color=KOROSTUS, ms=3.5,
            label="uusin simulaatiotila")
    ax.plot(ruutu, interp, "o-", color=TOINEN, ms=3.5, lw=1.0,
            label="interpoloitu")
    ax.set_xlabel("piirretty ruutu (144 Hz)")
    ax.set_ylabel("sijainti (pikseliä)")
    ax.legend(frameon=False)
    tallenna(fig, kohde, "interpolointi.png")


# --- Luku 5: 2D-grafiikka -------------------------------------------------

def piirto(a: Ajaja, kohde: Path) -> None:
    a.aja("05-piirto")
    atlas = lue_ppm(a.tyo / "atlas.ppm")
    ruutu = lue_ppm(a.tyo / "ruutu.ppm")
    fig, (ax, bx) = plt.subplots(
        1, 2, figsize=(6.6, 2.5),
        width_ratios=[atlas.shape[1] / atlas.shape[0] * 0.9,
                      ruutu.shape[1] / ruutu.shape[0]])
    for akseli, kuva, otsikko in ((ax, atlas, "atlas"),
                                  (bx, ruutu, "piirretty ruutu")):
        h, w = kuva.shape[:2]
        akseli.imshow(kuva, interpolation="nearest", extent=(0, w, h, 0))
        akseli.set_title(f"{otsikko} ({w} × {h} pikseliä)", fontsize=9)
        akseli.set_xticks(range(0, w + 1, 8 if w <= 32 else 16))
        akseli.set_yticks(range(0, h + 1, 8))
        akseli.tick_params(labelsize=7)
    for x in range(8, atlas.shape[1], 8):
        ax.axvline(x, color="white", lw=0.6, ls=":")
    tallenna(fig, kohde, "piirto.png")


def kamera(a: Ajaja, kohde: Path) -> None:
    d = np.array([list(map(float, r.split()))
                  for r in a.aja("05-piirto", "k").splitlines()])
    t, px, kx = d[:, 0] / 60.0, d[:, 1], d[:, 2]
    fig, ax = plt.subplots(figsize=(5.8, 2.8))
    ax.fill_between(t, kx, kx + 64, color=VAALEA, alpha=0.6, lw=0,
                    label="näkymä (64 pikseliä)")
    ax.fill_between(t, kx + 64 * 0.35, kx + 64 * 0.65, color="#C9D8EA",
                    lw=0, label="kuollut alue")
    ax.plot(t, px, color=KOROSTUS, lw=1.4, label="pelaaja")
    ax.set_xlabel("aika (s)")
    ax.set_ylabel("x maailmassa (pikseliä)")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    tallenna(fig, kohde, "kamera.png")


# --- Luku 6: harva joukko (periaatekuva) ------------------------------------

def harva_joukko(kohde: Path) -> None:
    harva = [None, 0, None, 2, 1, None, None]
    tihea = [1, 4, 3]
    fig, ax = plt.subplots(figsize=(5.6, 2.4))

    def rivi(y: float, arvot: list[str], otsikko: str, vari: str) -> None:
        ax.text(-0.3, y + 0.3, otsikko, ha="right", va="center", fontsize=8)
        for i, arvo in enumerate(arvot):
            ax.add_patch(Rectangle((i, y), 1, 0.6, fc=vari, ec=HARMAA,
                                   lw=0.8))
            ax.text(i + 0.5, y + 0.3, arvo, ha="center", va="center",
                    fontsize=8)

    rivi(2.2, ["–" if v is None else str(v) for v in harva],
         "harva: tunnus → paikka", "white")
    for i in range(len(harva)):
        ax.text(i + 0.5, 2.95, str(i), ha="center", fontsize=7,
                color=HARMAA)
    ax.text(len(harva) + 0.2, 2.95, "olion tunnus", fontsize=7,
            color=HARMAA, va="bottom")
    rivi(1.0, [str(v) for v in tihea], "tiheä: paikka → tunnus", "#C9D8EA")
    rivi(0.2, [f"v{v}" for v in tihea], "komponentit: paikka → nopeus",
         "#F0DCC0")
    for tunnus, paikka in enumerate(harva):
        if paikka is not None:
            ax.add_patch(FancyArrowPatch((tunnus + 0.5, 2.2),
                                         (paikka + 0.5, 1.6),
                                         arrowstyle="-|>", color=KOROSTUS,
                                         mutation_scale=8, lw=0.9))
    ax.set_xlim(-3.8, len(harva) + 1.8)
    ax.set_ylim(0, 3.3)
    ax.axis("off")
    tallenna(fig, kohde, "harva-joukko.png")


# --- Luku 7: törmäykset ----------------------------------------------------

def tormaysmuodot(kohde: Path) -> None:
    # Seinä, pelaajan koko ja pallot ovat esimerkin 07-muodot.cpp arvot;
    # pelaajan paikat ja siirrot luetaan sen testatusta tulosteesta.
    teksti = odotettu("07-muodot")
    luku = r"\((-?[\d.]+), (-?[\d.]+)\)"
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 3.4))
    for akseli in (ax, bx):
        akseli.add_patch(Rectangle((-1, -3), 2, 6, fc=VAALEA, ec=HARMAA))
        akseli.text(0, -2.5, "seinä", ha="center", fontsize=8)
        akseli.set_aspect("equal")
        akseli.set_xlim(-1.6, 5.0)
        akseli.tick_params(labelsize=7)
    for m in re.finditer(rf"pelaaja {luku}: törmää, siirretään {luku}",
                         teksti):
        x0, y0, x1, y1 = map(float, m.groups())
        ax.add_patch(Rectangle((x0 - 1, y0 - 1), 2, 2, fc="none",
                               ec=KOROSTUS, ls="--"))
        ax.add_patch(Rectangle((x1 - 1, y1 - 1), 2, 2, fc="none",
                               ec=TOINEN, lw=1.3))
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                     mutation_scale=9, color=TUMMA))
        ax.plot([x0], [y0], ".", color=KOROSTUS)
    for m in re.finditer(rf"pelaaja {luku}: ei törmää", teksti):
        x0, y0 = map(float, m.groups())
        ax.add_patch(Rectangle((x0 - 1, y0 - 1), 2, 2, fc="none",
                               ec=VIHREA))
    ax.set_ylim(-3.4, 5.4)
    ax.set_title("laatikot: katkoviiva ennen, yhtenäinen\n"
                 "erottavan siirtymän jälkeen", fontsize=8)
    pallo, toinen, r = (1.8, 3.8), (3.5, 3.8), 1.0
    lahin = (min(max(pallo[0], -1), 1), min(max(pallo[1], -3), 3))
    bx.add_patch(Circle(pallo, r, fc="none", ec=TOINEN, lw=1.3))
    bx.add_patch(Circle(toinen, r, fc="none", ec=KOROSTUS, lw=1.3))
    bx.plot(*zip(pallo, lahin), color=TUMMA, lw=0.9)
    bx.plot(*zip(pallo, toinen), color=TUMMA, lw=0.9, ls=":")
    bx.plot(*lahin, "s", color=TUMMA, ms=4)
    bx.plot(*zip(pallo, toinen), ".", color=TUMMA)
    etaisyys = float(re.search(r"etäisyys ([\d.]+)", teksti).group(1))
    bx.text(2.65, 4.0, f"{etaisyys:.2f} < 2".replace(".", ","),
            ha="center", fontsize=7)
    bx.text(1.05, 2.75, "lähin piste", fontsize=7, ha="left", va="top")
    bx.set_ylim(-3.4, 5.4)
    bx.set_title("ympyrät: etäisyys laatikon lähimpään\n"
                 "pisteeseen ja keskipisteiden väli", fontsize=8)
    tallenna(fig, kohde, "tormaysmuodot.png")


def ruudukko(kohde: Path) -> None:
    # Periaatekuva: 20 kappaletta samalla satunnaislukukaavalla kuin
    # esimerkissä 07-laajavaihe.cpp, ruudukko 6 × 6. Parit testataan,
    # kun kappaleet ovat samassa tai viereisessä solussa.
    tila = 12345

    def satunnainen() -> float:
        nonlocal tila
        tila = (tila * 1664525 + 1013904223) % 2**32
        return (tila >> 8) / 2**24

    pisteet = [(satunnainen() * 6, satunnainen() * 6) for _ in range(20)]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.2, 3.0))
    n = len(pisteet)
    parit = 0
    for i in range(n):
        for j in range(i + 1, n):
            ax.plot(*zip(pisteet[i], pisteet[j]), color=KOROSTUS, lw=0.3,
                    alpha=0.5)
            if (abs(int(pisteet[i][0]) - int(pisteet[j][0])) <= 1
                    and abs(int(pisteet[i][1]) - int(pisteet[j][1])) <= 1):
                bx.plot(*zip(pisteet[i], pisteet[j]), color=KOROSTUS,
                        lw=0.9)
                parit += 1
    for k in range(7):
        bx.axhline(k, color=HARMAA, lw=0.5)
        bx.axvline(k, color=HARMAA, lw=0.5)
    for akseli, otsikko in ((ax, f"kaikki parit: {n * (n - 1) // 2} testiä"),
                            (bx, "sama tai viereinen solu: "
                                 f"{parit} testiä")):
        for x, y in pisteet:
            akseli.add_patch(Circle((x, y), 0.17, fc="#C9D8EA", ec=TOINEN,
                                    zorder=3))
        akseli.set_xlim(0, 6)
        akseli.set_ylim(0, 6)
        akseli.set_aspect("equal")
        akseli.set_xticks([])
        akseli.set_yticks([])
        akseli.set_title(otsikko, fontsize=8)
        for sivu in akseli.spines.values():
            sivu.set_visible(True)
    tallenna(fig, kohde, "ruudukko.png")


def tunnelointi(kohde: Path) -> None:
    # Sama laskenta kuin esimerkissä 07-tunnelointi.cpp: seinä välillä
    # 10,0–10,2 m, askel 1/60 s. Tulos (osuu/ohi) luetaan tulosteesta.
    teksti = odotettu("07-tunnelointi")
    fig, ax = plt.subplots(figsize=(6.4, 1.9))
    ax.add_patch(Rectangle((10.0, -0.5), 0.2, 2.0, fc=HARMAA, ec="none"))
    ax.text(10.1, 1.62, "seinä 0,2 m", ha="center", fontsize=7)
    for y, nopeus, vari in ((1, 60, TOINEN), (0, 420, KOROSTUS)):
        xs = [i * nopeus / 60.0 for i in range(0, 20)
              if i * nopeus / 60.0 <= 15]
        ax.plot(xs, [y] * len(xs), "o-", color=vari, ms=4, lw=0.8)
        tulos = re.search(rf"{nopeus} m/s: askeleen lopussa (\w+)",
                          teksti).group(1)
        ax.text(15.3, y, f"{nopeus} m/s: {tulos}", va="center", fontsize=8,
                color=vari)
    ax.set_yticks([])
    ax.set_ylim(-0.5, 1.9)
    ax.set_xlim(-0.3, 19)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("paikka askeleen lopussa (m)")
    tallenna(fig, kohde, "tunnelointi.png")


# --- Luku 8: fysiikka ja törmäysvaste ---------------------------------------

def energia(a: Ajaja, kohde: Path) -> None:
    d = np.array([list(map(float, r.split()))
                  for r in a.aja("08-integraattorit", "k").splitlines()])
    t = d[:, 0]
    nimet = ("eksplisiittinen Euler", "semi-implisiittinen Euler",
             "nopeus-Verlet")
    varit = (KOROSTUS, TOINEN, VIHREA)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.8, 2.7))
    alku = t <= 3.0
    for i, (nimi, vari) in enumerate(zip(nimet, varit)):
        ax.plot(t[alku], d[alku, 1 + i], color=vari, lw=1.1, label=nimi)
        bx.plot(t, d[:, 4 + i], color=vari, lw=1.1)
    ax.plot(t[alku], np.cos(np.sqrt(40.0) * t[alku]), color=TUMMA, lw=0.7,
            ls=":", label="tarkka ratkaisu")
    ax.set_ylim(-4, 4)
    ax.set_xlabel("aika (s)")
    ax.set_ylabel("paikka (m)")
    ax.legend(frameon=False, fontsize=6.5, loc="lower left", ncols=2,
              bbox_to_anchor=(-0.05, 1.0))
    bx.set_yscale("log")
    bx.set_xlabel("aika (s)")
    bx.set_ylabel("energia / alkuenergia")
    tallenna(fig, kohde, "energia.png")


def hyppy(a: Ajaja, kohde: Path) -> None:
    sarjat: dict[int, list[tuple[float, float]]] = {}
    for r in a.aja("08-hyppy", "k").splitlines():
        n, ruutu, y = r.split()
        sarjat.setdefault(int(n), [(0.0, 0.0)]).append(
            (int(ruutu) / 60.0, max(float(y), 0.0)))
    nimet = ("pitkä painallus", "lyhyt painallus", "pitkä, raskas pudotus")
    fig, ax = plt.subplots(figsize=(5.4, 2.6))
    for (n, pisteet), vari in zip(sorted(sarjat.items()),
                                  (TOINEN, KOROSTUS, VIHREA)):
        ax.plot(*zip(*pisteet), color=vari, lw=1.3, label=nimet[n])
    ax.axhline(3.0, color=HARMAA, lw=0.6, ls=":")
    ax.text(0.01, 3.03, "suunniteltu huippu 3 m", ha="left", fontsize=7,
            color=HARMAA, va="bottom")
    ax.set_xlabel("aika (s)")
    ax.set_ylabel("korkeus (m)")
    ax.set_ylim(0, 3.5)
    ax.set_xlim(0, 1.15)
    ax.legend(frameon=False, fontsize=7, loc="center right")
    tallenna(fig, kohde, "hyppy.png")


def piirra_kartta(ax: plt.Axes, kartta: list[str]) -> None:
    for y, rivi in enumerate(kartta):
        for x, merkki in enumerate(rivi):
            if merkki == "#":
                ax.add_patch(Rectangle((x, y), 1, 1, fc=HARMAA,
                                       ec="white", lw=0.3))
            elif merkki == "~":
                ax.add_patch(Rectangle((x, y), 1, 1, fc="#C8D6B0",
                                       ec="white", lw=0.3, hatch="..."))
    ax.set_xlim(0, len(kartta[0]))
    ax.set_ylim(len(kartta), 0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def hahmo(a: Ajaja, kohde: Path) -> None:
    kartta, rata = [], []
    for r in a.aja("08-hahmo", "k").splitlines():
        if r.startswith("kartta "):
            kartta.append(r.split()[1])
        else:
            _, x, y, maassa = r.split()
            rata.append((float(x), float(y), maassa == "1"))
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    piirra_kartta(ax, kartta)
    xs = np.array([p[0] for p in rata])
    ys = np.array([p[1] for p in rata])
    maassa = np.array([p[2] for p in rata])
    ax.plot(xs, ys, color=VAALEA, lw=0.8, zorder=1)
    ax.plot(xs[maassa], ys[maassa], ".", color=TOINEN, ms=2.5,
            label="maassa")
    ax.plot(xs[~maassa], ys[~maassa], ".", color=KOROSTUS, ms=2.5,
            label="ilmassa")
    for i in (0, 61, 100, 133, 214):
        ax.add_patch(Rectangle((xs[i] - 0.4, ys[i] - 0.45), 0.8, 0.9,
                               fc="none", ec=TUMMA, lw=0.9, zorder=3))
    ax.legend(frameon=False, fontsize=7, loc="upper left", ncols=2,
              bbox_to_anchor=(0.05, 0.9))
    tallenna(fig, kohde, "hahmo.png")


# --- Luku 9: pelitekoäly ----------------------------------------------------

def reitinhaku(a: Ajaja, kohde: Path) -> None:
    kartta: list[str] = []
    tutkitut: dict[str, list[tuple[int, int]]] = {"dijkstra": [], "astar": []}
    polut: dict[str, list[tuple[int, int]]] = {"dijkstra": [], "astar": []}
    for r in a.aja("09-reitinhaku", "k").splitlines():
        osat = r.split()
        if osat[0] == "kartta":
            kartta.append(osat[1])
        elif osat[1] == "tutkittu":
            tutkitut[osat[0]].append((int(osat[3]), int(osat[4])))
        else:
            polut[osat[0]].append((int(osat[2]), int(osat[3])))
    fig, akselit = plt.subplots(2, 1, figsize=(6.2, 5.4))
    vari = plt.get_cmap("YlGnBu")
    for ax, avain, nimi in zip(akselit, ("dijkstra", "astar"),
                               ("Dijkstra", "A* (Manhattan)")):
        piirra_kartta(ax, kartta)
        n = len(tutkitut[avain])
        for i, (x, y) in enumerate(tutkitut[avain]):
            ax.add_patch(Rectangle((x, y), 1, 1, ec="white", lw=0.3,
                                   fc=vari(0.15 + 0.6 * i / n), zorder=0.5,
                                   alpha=0.9))
        px = [x + 0.5 for x, _ in polut[avain]]
        py = [y + 0.5 for _, y in polut[avain]]
        ax.plot(px, py, color=KOROSTUS, lw=1.6)
        for merkki in "AB":
            for y, rivi in enumerate(kartta):
                if merkki in rivi:
                    ax.text(rivi.index(merkki) + 0.5, y + 0.5, merkki,
                            ha="center", va="center", fontsize=8,
                            fontweight="bold", color="white",
                            bbox={"boxstyle": "circle,pad=0.15",
                                  "fc": TUMMA, "ec": "none"})
        ax.set_title(f"{nimi}: {n} tutkittua ruutua", fontsize=9)
    tallenna(fig, kohde, "reitinhaku.png")


def vartija(a: Ajaja, kohde: Path) -> None:
    kartta, rivit = [], []
    for r in a.aja("09-vartija", "k").splitlines():
        osat = r.split()
        if osat[0] == "kartta":
            kartta.append(osat[1])
        else:
            rivit.append((osat[1], int(osat[2]), int(osat[3]),
                          int(osat[4]), int(osat[5])))
    varit = {"partio": TOINEN, "takaa-ajo": KOROSTUS, "etsintä": KOLMAS}
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    piirra_kartta(ax, kartta)
    ax.plot([r[3] + 0.5 for r in rivit], [r[4] + 0.65 for r in rivit],
            color=TUMMA, lw=1.0, ls="--", label="pelaaja")
    for i in range(1, len(rivit)):
        tila = rivit[i][0]
        ax.plot([rivit[i - 1][1] + 0.5, rivit[i][1] + 0.5],
                [rivit[i - 1][2] + 0.35, rivit[i][2] + 0.35],
                color=varit[tila], lw=2.0, solid_capstyle="round")
    for tila, vari in varit.items():
        ax.plot([], [], color=vari, lw=2.0, label=f"vartija: {tila}")
    ax.plot(rivit[0][1] + 0.5, rivit[0][2] + 0.35, "o", color=TOINEN, ms=5)
    ax.plot(rivit[0][3] + 0.5, rivit[0][4] + 0.65, "s", color=TUMMA, ms=4)
    ax.plot(rivit[-1][3] + 0.5, rivit[-1][4] + 0.65, "s", color=TUMMA,
            ms=4, mfc="white")
    ax.legend(frameon=False, fontsize=7, loc="upper center", ncols=4,
              bbox_to_anchor=(0.5, -0.02))
    tallenna(fig, kohde, "vartija.png")


# --- Luku 11: ääni ------------------------------------------------------------

def miksaus(a: Ajaja, kohde: Path) -> None:
    sarjat: dict[str, list[tuple[float, int]]] = {}
    for r in a.aja("11-miksaus", "k").splitlines():
        v, i, arvo = r.split()
        sarjat.setdefault(v, []).append((int(i) / 48.0, int(arvo)))
    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    for v, vari in (("0.6", KOROSTUS), ("0.3", TOINEN)):
        ax.plot(*zip(*sarjat[v]), color=vari, lw=1.1,
                label=f"äänten voimakkuus {v.replace('.', ',')}")
    for raja in (-32767, 32767):
        ax.axhline(raja, color=HARMAA, lw=0.6, ls=":")
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("näytteen arvo (16 bittiä)")
    ax.legend(frameon=False, fontsize=7, loc="upper right", ncols=2,
              bbox_to_anchor=(1.0, 1.2))
    tallenna(fig, kohde, "miksaus.png")


# --- Luku 12: Kipinä ------------------------------------------------------------

def kipina(a: Ajaja, kohde: Path) -> None:
    """Neljä ruutua tallenteen varrelta: tallenne katkaistaan kohdasta."""
    tallenne = [(int(r.split()[0]), r.split()[1]) for r in
                (ESIM / "12-kipina.syote").read_text().splitlines()]
    fig, akselit = plt.subplots(1, 4, figsize=(6.8, 2.1))
    for ax, raja in zip(akselit, (60, 150, 300, 555)):
        jaljella, syote = raja, ""
        for ruutuja, napit in tallenne:
            n = min(ruutuja, jaljella)
            if n > 0:
                syote += f"{n} {napit}\n"
            jaljella -= n
        tuloste = a.aja("12-kipina", syote=syote)
        pisteet = re.search(r"pisteet (\d+)", tuloste).group(1)
        ax.imshow(lue_ppm(a.tyo / "kipina.ppm"), interpolation="nearest")
        ax.set_title(f"ruutu {raja}, pisteet {pisteet}", fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.subplots_adjust(wspace=0.05)
    tallenna(fig, kohde, "kipina-sarja.png")


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tyo:
        a = Ajaja(Path(tyo))
        aika_askel(a, kohde)
        interpolointi(a, kohde)
        piirto(a, kohde)
        kamera(a, kohde)
        harva_joukko(kohde)
        tormaysmuodot(kohde)
        ruudukko(kohde)
        tunnelointi(kohde)
        energia(a, kohde)
        hyppy(a, kohde)
        hahmo(a, kohde)
        reitinhaku(a, kohde)
        vartija(a, kohde)
        miksaus(a, kohde)
        kipina(a, kohde)


if __name__ == "__main__":
    main()
