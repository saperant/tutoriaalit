"""Piirtää paketin kuvat esimerkkien simulaatiolokeista.

Käyttö: python3 kuvat/piirra.py kuvat   (ajetaan komennolla `make kuvat`)

Skripti kääntää esimerkit väliaikaiseen hakemistoon ja ajaa ne
argumentilla k, jolloin ne tulostavat tavallisen tulosteensa lisäksi
tapahtumalokin (rivit alkavat merkillä @, ks. yhteinen/verkko.hpp).
Kuvat näyttävät siis saman simulaation, jonka tulosteen testit
tarkistavat. Kuvat ovat versionhallinnassa.
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
from matplotlib import font_manager
from matplotlib.patches import Rectangle

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
    def __init__(self, tyo: Path) -> None:
        self.tyo = tyo

    def loki(self, nimi: str) -> list[list[str]]:
        """Esimerkin lokirivit sanoiksi jaettuina."""
        binaari = self.tyo / nimi
        subprocess.run([KAANTAJA, "-std=c++23", "-O1", f"-I{ESIM}",
                        str(ESIM / f"{nimi}.cpp"), "-o", str(binaari)],
                       check=True)
        tuloste = subprocess.run([str(binaari), "k"], capture_output=True,
                                 text=True, check=True, cwd=self.tyo).stdout
        return [r[2:].split() for r in tuloste.splitlines()
                if r.startswith("@ ")]

    def tuloste(self, nimi: str) -> str:
        binaari = self.tyo / nimi
        subprocess.run([KAANTAJA, "-std=c++23", "-O1", f"-I{ESIM}",
                        str(ESIM / f"{nimi}.cpp"), "-o", str(binaari)],
                       check=True)
        return subprocess.run([str(binaari), "k"], capture_output=True,
                              text=True, check=True, cwd=self.tyo).stdout


def odotettu(nimi: str) -> str:
    return (ESIM / f"{nimi}.odotettu").read_text("utf-8")


def tallenna(fig: plt.Figure, kohde: Path, nimi: str) -> None:
    fig.savefig(kohde / nimi)
    plt.close(fig)
    print("kirjoitettu", nimi)


def kaistat(ax: plt.Axes, yla: str, ala: str, t0: float, t1: float) -> None:
    """Aika–paikka-kaavion pohja: kaksi osapuolta vaakaviivoina."""
    for y, nimi in ((1, yla), (0, ala)):
        ax.plot([t0, t1], [y, y], color=TUMMA, lw=1.0)
        ax.text(t0 - (t1 - t0) * 0.015, y, nimi, ha="right", va="center",
                fontsize=8)
    ax.set_xlim(t0, t1)
    ax.set_ylim(-0.45, 1.45)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("aika (ms)")


def nuoli(ax: plt.Axes, t0: float, y0: float, t1: float, y1: float,
          vari: str, lw: float = 0.9, katosi: bool = False) -> None:
    if katosi:
        tx, ty = t0 + (t1 - t0) * 0.55, y0 + (y1 - y0) * 0.55
        ax.plot([t0, tx], [y0, ty], color=vari, lw=lw, ls=":")
        ax.plot([tx], [ty], "x", color=vari, ms=5, mew=1.2)
    else:
        ax.annotate("", (t1, y1), (t0, y0),
                    arrowprops={"arrowstyle": "-|>", "color": vari,
                                "lw": lw, "shrinkA": 0, "shrinkB": 0,
                                "mutation_scale": 7})


# --- Luku 1 ---------------------------------------------------------------

def ping(kohde: Path) -> None:
    rivi = odotettu("01-ping").splitlines()[0]
    parit = dict((int(a), int(b)) for a, b in re.findall(r"(\d+):(\d+)",
                                                         rivi))
    fig, ax = plt.subplots(figsize=(5.8, 2.2))
    ax.vlines(list(parit), 0, list(parit.values()), color=TOINEN, lw=1.4)
    ax.plot(list(parit), list(parit.values()), "o", color=TOINEN, ms=4)
    kadonneet = [i for i in range(20) if i not in parit]
    ax.plot(kadonneet, [4] * len(kadonneet), "x", color=KOROSTUS, ms=7,
            mew=1.6, label="vastaus ei saapunut")
    ax.set_xticks(range(0, 20))
    ax.tick_params(axis="x", labelsize=7)
    ax.set_xlabel("pingin numero")
    ax.set_ylabel("kiertoviive (ms)")
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, fontsize=7, loc="upper right",
              bbox_to_anchor=(1.0, 1.15))
    tallenna(fig, kohde, "ping.png")


# --- Luku 3 ---------------------------------------------------------------

def jonopaa(a: Ajaja, kohde: Path) -> None:
    rivit = [list(map(int, r)) for r in a.loki("03-jonopaa")]
    vali = 50
    udp = [r[1] for r in rivit]
    tcp = [r[2] for r in rivit]
    # Ensimmäinen ikkuna, jossa paketti katoaa (UDP:llä -1).
    k0 = next(k for k in range(30, len(udp)) if udp[k] < 0)
    t0, t1 = (k0 - 6) * vali, (k0 + 12) * vali

    def ika(saapuu: list[int]) -> tuple[list[int], list[int]]:
        ajat, iat = [], []
        uusin = k0 - 12
        for t in range(t0, t1):
            for k in range(uusin + 1, k0 + 14):
                if 0 <= saapuu[k] <= t:
                    uusin = k
            ajat.append(t)
            iat.append(t - uusin * vali)
        return ajat, iat

    fig, ax = plt.subplots(figsize=(6.2, 2.6))
    ax.plot(*ika(tcp), color=KOROSTUS, lw=1.3, label="TCP")
    ax.plot(*ika(udp), color=TOINEN, lw=1.3, label="UDP")
    ax.axvline(k0 * vali, color=HARMAA, lw=0.7, ls=":")
    ax.text(k0 * vali + 6, 12, f"paketti {k0} katoaa", fontsize=7,
            color=HARMAA)
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("näytetyn tilan ikä (ms)")
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    tallenna(fig, kohde, "jonopaa.png")


# --- Luku 4 ---------------------------------------------------------------

def paketti(kohde: Path) -> None:
    """Paketin otsake ja kuittauskentän tulkinta (periaatekuva)."""
    fig, ax = plt.subplots(figsize=(6.6, 2.3))
    x = 0.0
    for nimi, bitit, leveys, vari in (
            ("numero", "16 b", 2, "#C9D8EA"), ("kuittaus", "16 b", 2,
                                               "#C9D8EA"),
            ("kuittauskenttä", "32 b", 4, "#C9D8EA"),
            ("tapahtumat", "luotettavat", 3, "#F0DCC0"),
            ("tila", "ei uudelleen", 3, VAALEA)):
        ax.add_patch(Rectangle((x, 2.0), leveys, 0.8, fc=vari, ec=HARMAA))
        ax.text(x + leveys / 2, 2.52, nimi, ha="center", fontsize=8)
        ax.text(x + leveys / 2, 2.17, bitit, ha="center", fontsize=6.5,
                color=HARMAA)
        x += leveys
    ax.text(0, 1.35, "Esimerkki: kuittaus = 105, kentän bitit 0–7 = "
            "1 1 0 1 1 1 0 1", fontsize=8)
    saapui = [1, 1, 0, 1, 1, 1, 0, 1]
    ax.add_patch(Rectangle((0, 0.2), 1.3, 0.7, fc="#C9E3D2", ec=HARMAA))
    ax.text(0.65, 0.55, "105", ha="center", va="center", fontsize=8)
    for i, bitti in enumerate(saapui):
        vari = "#C9E3D2" if bitti else "#EFC9C9"
        ax.add_patch(Rectangle((1.5 + i * 1.3, 0.2), 1.3, 0.7, fc=vari,
                               ec=HARMAA))
        ax.text(2.15 + i * 1.3, 0.55, f"{104 - i}", ha="center",
                va="center", fontsize=8)
        ax.text(2.15 + i * 1.3, 0.02, "saapui" if bitti else "puuttuu",
                ha="center", va="top", fontsize=6.5,
                color=VIHREA if bitti else KOROSTUS)
    ax.text(12.1, 0.55, "… 73", va="center", fontsize=8)
    ax.set_xlim(-0.2, 14.2)
    ax.set_ylim(-0.4, 3.0)
    ax.axis("off")
    tallenna(fig, kohde, "paketti.png")


def kattely(a: Ajaja, kohde: Path) -> None:
    nimet = ["pyyntö", "haaste", "vastaus", "hyväksytty", "elossa"]
    varit = [TOINEN, KOROSTUS, TOINEN, KOROSTUS, HARMAA]
    rivit = [r for r in a.loki("04-yhteys") if int(r[2]) <= 1100]
    fig, ax = plt.subplots(figsize=(6.8, 2.4))
    kaistat(ax, "asiakas", "palvelin", 0, 1100)
    for suunta, y0, y1 in (("ylos", 1, 0), ("alas", 0, 1)):
        lahetetyt = [(int(r[2]), int(r[3])) for r in rivit
                     if r[0] == "L" and r[1] == suunta]
        saapuneet = [(int(r[2]), int(r[3])) for r in rivit
                     if r[0] == "V" and r[1] == suunta]
        for t, tyyppi in lahetetyt:
            # Viive on 40–60 ms: saapuminen on ensimmäinen samaa tyyppiä
            # oleva vastaanotto sillä välillä.
            perilla = [s for s, ty in saapuneet
                       if ty == tyyppi and 40 <= s - t <= 60]
            nuoli(ax, t, y0, perilla[0] if perilla else t + 50, y1,
                  varit[tyyppi], katosi=not perilla)
            ax.text(t, y0 + (0.12 if y0 else -0.12), nimet[tyyppi],
                    fontsize=6.5, ha="left", va="bottom" if y0 else "top",
                    color=varit[tyyppi], rotation=25 if y0 else -25)
    tallenna(fig, kohde, "kattely.png")


def kuittaukset(a: Ajaja, kohde: Path) -> None:
    rivit = a.loki("04-kuittaukset")
    tapahtumat: dict[int, list[int]] = {}   # paketti -> tapahtumat
    for r in rivit:
        if r[0] == "E":
            tapahtumat.setdefault(int(r[1]), []).append(int(r[2]))
    kerrat: dict[int, list[int]] = {}
    for numero, lista in tapahtumat.items():
        for t in lista:
            kerrat.setdefault(t, []).append(numero)
    lahetys = {(r[1], int(r[3])): int(r[2]) for r in rivit if r[0] == "L"}
    kuittaus = {(r[1], int(r[3])): int(r[4]) for r in rivit if r[0] == "L"}
    saapui = {(r[1], int(r[3])): int(r[2]) for r in rivit if r[0] == "V"}
    # Ensimmäinen tapahtuma, jonka ensimmäinen paketti katosi matkalla.
    tapahtuma, paketit = next((t, p) for t, p in sorted(kerrat.items())
                              if len(p) > 1 and ("ylos", p[0]) not in saapui)
    t0 = lahetys[("ylos", paketit[0])] - 50
    t1 = lahetys[("ylos", paketit[-1])] + 190
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    kaistat(ax, "asiakas", "palvelin", t0, t1)
    for (suunta, numero), t in sorted(lahetys.items(), key=lambda x: x[1]):
        if not t0 <= t <= t1 - 60:
            continue
        ylos = suunta == "ylos"
        kantaa = ylos and tapahtuma in tapahtumat.get(numero, [])
        vari = (KOROSTUS if kantaa else TOINEN) if ylos else HARMAA
        perilla = saapui.get((suunta, numero))
        nuoli(ax, t, 1 if ylos else 0, perilla or t + 55, 0 if ylos else 1,
              vari, lw=1.4 if kantaa else 0.7, katosi=perilla is None)
        if ylos:
            ax.text(t, 1.08, f"#{numero}", fontsize=6.5, ha="center",
                    color=vari, fontweight="bold" if kantaa else "normal")
        else:
            ax.text(t, -0.1, f"k {kuittaus[(suunta, numero)]}",
                    fontsize=6, ha="center", va="top", color=HARMAA)
    ax.text(t0 + 5, 1.32, f"punaiset paketit kuljettavat tapahtuman "
            f"{tapahtuma}", fontsize=7, color=KOROSTUS)
    ax.text(t0 + 5, -0.38, "k n = palvelimen paketti kuittaa asiakkaan "
            "paketin n (ja 32 sitä edeltävää kentässä)", fontsize=7,
            color=HARMAA)
    tallenna(fig, kohde, "kuittaukset.png")


# --- Luku 5 ---------------------------------------------------------------

def kaista(kohde: Path) -> None:
    nimet, arvot = [], []
    for r in odotettu("05-vedokset").splitlines():
        m = re.match(r"(.+?)\s+(\d+) tavua/vedos\s+([\d.]+) kbit/s", r)
        nimet.append(m.group(1))
        arvot.append(float(m.group(3)))
    fig, ax = plt.subplots(figsize=(5.6, 2.2))
    palkit = ax.barh(nimet[::-1], arvot[::-1], color=TOINEN, height=0.6)
    ax.bar_label(palkit, [f"{v:.1f}".replace(".", ",")
                          for v in arvot[::-1]], padding=3, fontsize=8)
    ax.set_xlabel("kaista pelaajaa kohti (kbit/s)")
    ax.set_xlim(0, max(arvot) * 1.12)
    tallenna(fig, kohde, "kaista.png")


# --- Luku 6 ---------------------------------------------------------------

def tasmaytys(a: Ajaja, kohde: Path) -> None:
    tapaukset: dict[str, list[list[str]]] = {}
    nimi = ""
    for r in a.loki("06-ennustus"):
        if r[0] == "tapaus":
            nimi = " ".join(r[1:])
            tapaukset[nimi] = []
        else:
            tapaukset[nimi].append(r)
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(6.8, 5.0),
                                 height_ratios=[1, 1.15])
    # (a) Syötteiden ja tilojen kulku hyvällä yhteydellä.
    hyva = tapaukset["hyvä yhteys"]
    kasitelty = {int(r[1]): int(r[2]) for r in hyva if r[0] == "P"}
    tilat = [(int(r[1]), int(r[2]), int(r[4])) for r in hyva
             if r[0] == "T"]
    t1 = 400
    kaistat(ax, "asiakas", "palvelin", 0, t1)
    valittu = 5
    for n, t in kasitelty.items():
        if n * 20 > t1 - 60:
            continue
        oma = n == valittu
        nuoli(ax, n * 20, 1, t, 0, KOROSTUS if oma else TOINEN,
              lw=1.5 if oma else 0.6)
        ax.text(n * 20, 1.07, str(n), fontsize=6.5, ha="center",
                color=KOROSTUS if oma else TOINEN,
                fontweight="bold" if oma else "normal")
    nahty: set[int] = set()
    for t, k, jonossa in tilat:
        if k in nahty or k == 0 or t > t1:
            continue
        nahty.add(k)
        oma = k == valittu
        nuoli(ax, kasitelty[k], 0, t, 1, KOROSTUS if oma else HARMAA,
              lw=1.5 if oma else 0.6)
        if oma:
            ax.text(t, 1.42, f"tila, käsitelty {k}: syötteet {k + 1}–"
                    f"{k + jonossa} simuloidaan uudelleen", fontsize=7,
                    color=KOROSTUS, ha="center")
            ax.plot([t, t], [1.0, 1.38], color=KOROSTUS, lw=0.6, ls=":")
    ax.set_ylim(-0.45, 1.7)
    ax.text(2, -0.3, "asiakkaan syötteet (numerot) ylhäältä alas, "
            "palvelimen tilat alhaalta ylös", fontsize=7, color=HARMAA)
    # (b) Sijainnit tönäisyn ympärillä.
    tonaisy = tapaukset["tönäisy"]
    ajat = [int(r[1]) for r in tonaisy if r[0] == "X"]
    ennuste = [int(r[2]) for r in tonaisy if r[0] == "X"]
    palvelin = [int(r[3]) for r in tonaisy if r[0] == "X"]
    vahv_t = [int(r[1]) for r in tonaisy if r[0] == "T"]
    vahv_x = [int(r[3]) for r in tonaisy if r[0] == "T"]
    lo, hi = 5300, 6400
    valinta = [i for i, t in enumerate(ajat) if lo <= t <= hi]
    bx.step([ajat[i] for i in valinta], [palvelin[i] for i in valinta],
            where="post", color=TUMMA, lw=1.0, label="palvelimen tila")
    v = [i for i, t in enumerate(vahv_t) if lo <= t <= hi]
    bx.step([vahv_t[i] for i in v], [vahv_x[i] for i in v], where="post",
            color=HARMAA, lw=1.0, ls="--",
            label="uusin asiakkaalle saapunut tila")
    bx.step([ajat[i] for i in valinta], [ennuste[i] for i in valinta],
            where="post", color=KOROSTUS, lw=1.4,
            label="asiakkaan ennuste (näytetään)")
    bx.axvline(6000, color=HARMAA, lw=0.6, ls=":")
    bx.set_xlim(lo, hi)
    bx.set_xlabel("aika (ms)")
    bx.set_ylabel("sijainti (cm)")
    bx.text(6005, min(ennuste[i] for i in valinta), "tönäisy",
            fontsize=7, color=HARMAA, va="bottom")
    bx.legend(frameon=False, fontsize=7, loc="lower left", ncols=3,
              bbox_to_anchor=(0, 1.0))
    fig.subplots_adjust(hspace=0.5)
    tallenna(fig, kohde, "tasmaytys.png")


def tikit(a: Ajaja, kohde: Path) -> None:
    rivit = a.loki("06-tikit")
    k = [list(map(int, r[1:])) for r in rivit if r[0] == "K"]
    t = [list(map(int, r[1:])) for r in rivit if r[0] == "T"]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.8, 2.6))
    ax.plot([r[0] / 1000 for r in k], [r[2] for r in k], ".", color=HARMAA,
            ms=3, label="yksittäinen näyte")
    ax.plot([r[0] / 1000 for r in k], [r[3] for r in k], color=KOROSTUS,
            lw=1.2, label="pienin kiertoviive 8:sta")
    ax.axhline(0, color=TUMMA, lw=0.5)
    ax.set_xlabel("aika (s)")
    ax.set_ylabel("kellon arvion virhe (ms)")
    ax.legend(frameon=False, fontsize=6.5, loc="lower left", ncols=1,
              bbox_to_anchor=(0, 1.0))
    bx.plot([r[0] / 1000 for r in t], [r[1] for r in t], color=TOINEN,
            lw=1.0)
    bx.axhline(2, color=HARMAA, lw=0.6, ls=":")
    bx.axvline(10, color=HARMAA, lw=0.6, ls=":")
    bx.text(10.15, -2.8, "viive kasvaa\n40 ms", fontsize=6.5, color=HARMAA)
    nopea = [r[0] / 1000 for r in t if r[2] == 19]
    bx.plot(nopea, [3.6] * len(nopea), "|", color=KOROSTUS, ms=5)
    bx.text(0.2, 3.9, "tikki 19 ms (asiakas kirii)", fontsize=6.5,
            color=KOROSTUS)
    bx.set_ylim(-3.2, 4.6)
    bx.set_xlabel("aika (s)")
    bx.set_ylabel("syötteen etumatka (tikkiä)")
    fig.subplots_adjust(wspace=0.32)
    tallenna(fig, kohde, "tikit.png")


# --- Luku 7 ---------------------------------------------------------------

def interpolointi(a: Ajaja, kohde: Path) -> None:
    rivit = a.loki("07-interpolointi")
    vedokset = [(int(r[3]), int(r[2])) for r in rivit if r[0] == "V"]
    sarjat: dict[int, list[tuple[int, int]]] = {}
    tosi: list[tuple[int, int]] = []
    for r in rivit:
        if r[0] == "N":
            sarjat.setdefault(int(r[1]), []).append((int(r[2]), int(r[3])))
            if r[1] == "0":
                tosi.append((int(r[2]), int(r[4])))
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.plot(*zip(*tosi), color=TUMMA, lw=0.9, ls=":",
            label="todellinen paikka")
    ax.plot(*zip(*vedokset), "o", color=HARMAA, ms=3, mfc="white",
            label="vedos saapuessaan")
    for tapa, nimi, vari in ((0, "uusin vedos", HARMAA),
                             (1, "ekstrapolointi", KOROSTUS),
                             (4, "interpolointi, puskuri 150 ms", TOINEN)):
        if tapa == 0:
            ax.step(*zip(*sarjat[tapa]), where="post", color=vari, lw=0.8,
                    label=nimi)
        else:
            ax.plot(*zip(*sarjat[tapa]), color=vari, lw=1.3, label=nimi)
    ax.set_xlim(3000, 5200)
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("paikka (mm)")
    ax.legend(frameon=False, fontsize=7, loc="lower left", ncols=3,
              bbox_to_anchor=(0, 1.0))
    tallenna(fig, kohde, "interpolointi.png")


# --- Luku 8 ---------------------------------------------------------------

def takaisinkelaus(a: Ajaja, kohde: Path) -> None:
    rivit = a.loki("08-takaisinkelaus")
    rata = [(int(r[1]), int(r[2])) for r in rivit if r[0] == "X"]
    laukaukset = [list(map(int, r[1:])) for r in rivit if r[0] == "L"]
    # Ensimmäinen laukaus, jonka kohde on palvelimen nykyhetkessä jo
    # seinän takana (x >= 1000), mutta johon kelaus osuu.
    t, nakyi, tahtays, hetki, kelattu, nyt_x = next(
        l for l in laukaukset if l[5] >= 1000 and abs(l[2] - l[4]) <= 200)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ikkuna = [(x, y) for x, y in rata if t - 900 <= x <= t + 300]
    ax.axhspan(1000, 1250, color=VAALEA, lw=0)
    ax.text(t - 880, 1125, "seinän takana", fontsize=7, color=HARMAA,
            va="center")
    ax.plot(*zip(*ikkuna), color=TUMMA, lw=1.2,
            label="kohde palvelimella")
    ax.plot([nakyi], [tahtays], "o", color=TOINEN, ms=6,
            label="ampujan näkemä kohde (tähtäys)")
    ax.plot([t], [nyt_x], "s", color=KOROSTUS, ms=6,
            label="kohde, kun laukaus saapuu")
    ax.annotate("", (hetki, kelattu + 25), (t, nyt_x + 25),
                arrowprops={"arrowstyle": "-|>", "color": VIHREA, "lw": 1.3,
                            "connectionstyle": "arc3,rad=0.25"})
    ax.text((hetki + t) / 2, nyt_x + 150, f"kelaus {t - hetki} ms",
            color=VIHREA, fontsize=7.5, ha="center")
    ax.vlines(nakyi, tahtays - 200, tahtays + 200, color=TOINEN, lw=3,
              alpha=0.35)
    ax.text(nakyi - 15, tahtays - 215, "osuma-alue", fontsize=7,
            color=TOINEN, ha="right")
    ax.set_xlabel("palvelimen aika (ms)")
    ax.set_ylabel("kohteen paikka (mm)")
    ax.set_ylim(0, 1420)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, kohde, "takaisinkelaus.png")


# --- Luku 9 ---------------------------------------------------------------

def lukitusaskel(a: Ajaja, kohde: Path) -> None:
    rivit = a.loki("09-lukitusaskel")
    fig, akselit = plt.subplots(2, 1, figsize=(6.8, 4.2), sharex=True)
    ruudut = range(62, 72)
    for ax, viive in zip(akselit, (0, 4)):
        saapui = {int(r[2]): int(r[3]) for r in rivit
                  if r[0] == "S" and int(r[1]) == viive}
        ajettu = {int(r[2]): int(r[3]) for r in rivit
                  if r[0] == "A" and int(r[1]) == viive}
        kaistat(ax, "vastustaja", "oma kone", 62 * 16 - 80, 72 * 16 + 50)
        ax.set_ylim(-0.7, 1.45)
        ax.text(62 * 16 - 83, -0.45, "aikataulu", ha="right", va="center",
                fontsize=8)
        for f in ruudut:
            lahti = (f - viive) * 16
            nuoli(ax, lahti, 1, saapui[f], 0, TOINEN, lw=0.8)
            aikataulu = f * 16
            myohassa = ajettu[f] > aikataulu
            vari = KOROSTUS if myohassa else VIHREA
            ax.plot([aikataulu], [-0.45], "|", color=TUMMA, ms=8)
            ax.text(aikataulu, -0.62, str(f), fontsize=6, ha="center",
                    va="top", color=TUMMA)
            ax.plot([aikataulu, ajettu[f]], [-0.45, 0], color=vari, lw=1.0)
            ax.plot([ajettu[f]], [0], "o", ms=4, color=vari)
            ax.text(lahti, 1.08, str(f), fontsize=6.5, ha="center",
                    color=TOINEN)
        ax.set_title(f"syöteviive {viive} ruutua: "
                     + ("jokainen ruutu odottaa syötettä" if viive == 0
                        else "syöte on perillä ennen ruudun aikaa"),
                     fontsize=8, loc="left")
        if viive == 0:
            ax.set_xlabel("")
    tallenna(fig, kohde, "lukitusaskel.png")


def rollback(a: Ajaja, kohde: Path) -> None:
    rivit = a.loki("09-rollback")
    fig, ax = plt.subplots(figsize=(6.8, 2.2))
    lo, hi = 0, 50
    ruudut = [int(r[3]) for r in rivit
              if r[0] == "R" and r[1] == "0" and lo <= int(r[3]) <= hi]
    ax.plot(ruudut, [0] * len(ruudut), "s", color=VAALEA, ms=6, mec=HARMAA,
            mew=0.5, label="ruutu ajettu aikataulussa arvatulla syötteellä")
    n = 0
    for r in rivit:
        if r[0] != "P" or r[1] != "0" or not lo <= int(r[4]) <= hi:
            continue
        palaa, ruutu = int(r[3]), int(r[4])
        y = 0.28 + 0.2 * (n % 2)
        ax.annotate("", (palaa - 0.4, y), (ruutu - 0.6, y),
                    arrowprops={"arrowstyle": "-|>", "color": KOROSTUS,
                                "lw": 1.6, "shrinkA": 0, "shrinkB": 0,
                                "mutation_scale": 8})
        ax.plot([ruutu - 0.6, ruutu - 0.6], [0.08, y], color=KOROSTUS,
                lw=0.6, ls=":")
        n += 1
    ax.plot([], [], color=KOROSTUS, lw=1.6,
            label="palautus: väärin arvatut ruudut lasketaan uudelleen")
    ax.set_ylim(-0.3, 1.25)
    ax.set_xlim(lo - 1, hi + 1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("ruutu")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    tallenna(fig, kohde, "rollback.png")


# --- Luku 12 --------------------------------------------------------------

def elo(a: Ajaja, kohde: Path) -> None:
    rivit = [r.split() for r in a.tuloste("12-elo").splitlines()[1:]]
    ottelut = [int(r[0]) for r in rivit]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 2.5))
    ax.plot(ottelut, [float(r[1]) for r in rivit], color=TOINEN, lw=1.3)
    ax.set_xlabel("otteluita pelaajaa kohti")
    ax.set_ylabel("luokituksen virhe (keskim.)")
    ax.set_ylim(0, None)
    bx.plot(ottelut, [int(r[2]) for r in rivit], color=TOINEN, lw=1.0,
            label="luokituksen mukaan")
    bx.plot(ottelut, [int(r[4]) for r in rivit], color=HARMAA, lw=0.8,
            label="satunnaisesti")
    bx.set_xlabel("otteluita pelaajaa kohti")
    bx.set_ylabel("tasaisia otteluita (%)")
    bx.set_ylim(0, 100)
    bx.legend(frameon=False, fontsize=7, loc="upper left")
    fig.subplots_adjust(wspace=0.3)
    tallenna(fig, kohde, "elo.png")


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tyo:
        a = Ajaja(Path(tyo))
        ping(kohde)
        jonopaa(a, kohde)
        paketti(kohde)
        kattely(a, kohde)
        kuittaukset(a, kohde)
        kaista(kohde)
        tasmaytys(a, kohde)
        tikit(a, kohde)
        interpolointi(a, kohde)
        takaisinkelaus(a, kohde)
        lukitusaskel(a, kohde)
        rollback(a, kohde)
        elo(a, kohde)


if __name__ == "__main__":
    main()
