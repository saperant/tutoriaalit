"""Piirtää paketin kuvat työkalujen raporteista ja simuloidun kortin ajosta.

Käyttö: python3 kuvat/piirra.py esimerkit/rakennus kuvat
(ajetaan komennolla `make kuvat`, joka tuottaa ensin lähtötiedot)

Lähtötiedot ovat samat Yosysin ja nextpnr:n raportit, jotka esimerkkien
testit tarkistavat, sekä nextpnr:n kirjoittamat sijoittelut ja simuloidun
kortin tallentamat kehykset. Kuvat ovat versionhallinnassa.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

KOROSTUS = "#B04848"
TOINEN = "#2F5F9A"
KOLMAS = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#D9E0E3"
# Sama kirjasin kuin PDF:n muissa kaavioissa, jos se on asennettu.
FONTIT = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({"font.family": "Inter" if "Inter" in FONTIT
                     else "DejaVu Sans",
                     "font.size": 9, "figure.dpi": 100, "savefig.dpi": 200,
                     "savefig.bbox": "tight", "axes.spines.top": False,
                     "axes.spines.right": False})


def lue(polku: Path) -> Any:
    return json.loads(polku.read_text("utf-8"))


def fmax(pnr: dict[str, Any]) -> float:
    """Kellon saavutettu taajuus (suunnitelmissa on yksi kello)."""
    arvot = [v["achieved"] for k, v in pnr["fmax"].items()
             if not k.startswith("$")]
    return float(min(arvot))


# --- Simuloidun kortin kehykset ------------------------------------------

def lue_ppm(polku: Path) -> np.ndarray:
    data = polku.read_bytes()
    osat = data.split(maxsplit=4)
    w, h = int(osat[1]), int(osat[2])
    return np.frombuffer(osat[4][:w * h * 3], dtype=np.uint8).reshape(h, w, 3)


def kehykset(r: Path, kohde: Path) -> None:
    """Kolme kehystä rinnakkain ja yksi täysikokoisena."""
    numerot = [2, 14, 26]
    ajat = [49, 249, 450]
    fig, akselit = plt.subplots(1, 3, figsize=(9.0, 2.5))
    for ax, n, t in zip(akselit, numerot, ajat):
        ax.imshow(lue_ppm(r / "kuvat" / f"kehys-{n:02d}.ppm"),
                  interpolation="lanczos")
        ax.set_title(f"kehys {n} ({t} ms)", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(True)
            s.set_color(HARMAA)
    fig.subplots_adjust(wspace=0.04)
    fig.savefig(kohde / "kehykset.png")
    plt.close(fig)
    plt.imsave(kohde / "kehys.png", lue_ppm(r / "kuvat" / "kehys-26.ppm"))


# --- Resurssit -----------------------------------------------------------

SUUNNITELMAT = [
    ("vilkku-raportti", "vilkku (luku 1)"),
    ("kertyma", "kertymä (luku 2)"),
    ("muisti-synk", "muisti, synkroninen luku (luku 4)"),
    ("muisti-komb", "muisti, kombinaatioluku (luku 4)"),
    ("kertoja-dsp", "kertoja, DSP-lohko (luku 4)"),
    ("kertoja-lut", "kertoja, logiikkasolut (luku 4)"),
    ("suodin-rinnakkain", "suodin, rinnakkainen (luku 9)"),
    ("suodin-jaettu", "suodin, jaettu kertoja (luku 9)"),
    ("kortti", "esittelysuunnitelma (luku 10)"),
    ("debug", "virheenjäljitysydin (luku 11)"),
]


def resurssit(r: Path, kohde: Path) -> None:
    """Logiikkasolujen käyttö suunnitelmittain, logaritminen asteikko."""
    nimet, solut, lisat = [], [], []
    for tiedosto, nimi in SUUNNITELMAT:
        u = lue(r / f"{tiedosto}.pnr.json")["utilization"]
        nimet.append(nimi)
        solut.append(u["ICESTORM_LC"]["used"])
        lisa = []
        if u["ICESTORM_RAM"]["used"]:
            lisa.append(f"{u['ICESTORM_RAM']['used']} lohko-RAM")
        if u["ICESTORM_DSP"]["used"]:
            lisa.append(f"{u['ICESTORM_DSP']['used']} DSP")
        if u["ICESTORM_PLL"]["used"]:
            lisa.append("PLL")
        lisat.append(" + " + ", ".join(lisa) if lisa else "")
    kapasiteetti = 5280
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    y = np.arange(len(nimet))[::-1]
    ax.barh(y, solut, color=KOROSTUS, height=0.62)
    for yi, n, liite in zip(y, solut, lisat):
        osuus = f"{100 * n / kapasiteetti:.1f}".replace(".", ",")
        if n > 500:         # pitkän palkin teksti palkin sisään
            ax.text(n / 1.12, yi, f"{n} ({osuus} %){liite}", va="center",
                    ha="right", fontsize=8, color="white")
        else:
            ax.text(n * 1.12, yi, f"{n} ({osuus} %){liite}", va="center",
                    fontsize=8, color="#1F2A2E")
    ax.axvline(kapasiteetti, color=HARMAA, lw=1, ls="--")
    ax.text(kapasiteetti * 0.93, len(nimet) - 0.45, "piirin 5 280 solua",
            ha="right", va="bottom", fontsize=8, color=HARMAA)
    ax.set_xscale("log")
    ax.set_xlim(1, 30000)
    ax.set_yticks(y, nimet)
    ax.set_xlabel("logiikkasoluja (logaritminen asteikko)")
    ax.tick_params(axis="y", length=0)
    fig.savefig(kohde / "resurssit.png")
    plt.close(fig)


# --- Kriittinen polku ----------------------------------------------------

LAJIT = [("clk-to-q", "kiikun lähtö", HARMAA),
         ("logic", "logiikka", KOROSTUS),
         ("routing", "reititys", TOINEN),
         ("setup", "asetusaika", KOLMAS)]


def kriittinen(pnr: dict[str, Any]) -> list[dict[str, Any]]:
    """Kellon sisäinen kriittinen polku (kiikulta kiikulle)."""
    for polku in pnr["critical_paths"]:
        if polku["from"] == polku["to"] and "async" not in polku["from"]:
            jaksot: list[dict[str, Any]] = polku["path"]
            return jaksot
    raise SystemExit("kriittistä polkua ei löydy")


def polut(r: Path, kohde: Path) -> None:
    """Kriittisen polun viive osiin jaettuna neljälle suunnitelmalle."""
    rivit = [("liukuhihna-1", "kertoja, 1 vaihe"),
             ("liukuhihna-1-retime", "kertoja, 1 vaihe + retime"),
             ("liukuhihna-2", "kertoja, 2 vaihetta"),
             ("kortti", "esittelysuunnitelma")]
    fig, ax = plt.subplots(figsize=(7.2, 2.3))
    y = np.arange(len(rivit))[::-1]
    for yi, (tiedosto, _) in zip(y, rivit):
        pnr = lue(r / f"{tiedosto}.pnr.json")
        summat = {laji: 0.0 for laji, _, _ in LAJIT}
        for osa in kriittinen(pnr):
            summat[osa["type"]] = summat.get(osa["type"], 0.0) + osa["delay"]
        vasen = 0.0
        for laji, _, vari in LAJIT:
            ax.barh(yi, summat[laji], left=vasen, color=vari, height=0.6)
            if summat[laji] > 2.0:
                ax.text(vasen + summat[laji] / 2, yi,
                        f"{summat[laji]:.1f}".replace(".", ","),
                        ha="center", va="center", color="white", fontsize=8)
            vasen += summat[laji]
        mhz = f"{fmax(pnr):.0f}"
        ax.text(vasen + 0.4, yi, f"{mhz} MHz", va="center", fontsize=8)
    ax.set_yticks(y, [nimi for _, nimi in rivit])
    ax.set_xlabel("kriittisen polun viive (ns)")
    ax.set_xlim(0, 36)
    ax.tick_params(axis="y", length=0)
    kahvat = [Rectangle((0, 0), 1, 1, color=v) for _, _, v in LAJIT]
    ax.legend(kahvat, [n for _, n, _ in LAJIT], ncol=4, frameon=False,
              loc="lower center", bbox_to_anchor=(0.45, 1.0), fontsize=8)
    fig.savefig(kohde / "polku.png")
    plt.close(fig)


# --- Sijoittelu ----------------------------------------------------------

# iCE40 UP5K: ruudukko 26 x 32; lohko-RAMit sarakkeissa 6 ja 19,
# DSP-lohkot ja IP-lohkot reunasarakkeissa 0 ja 25, IO ylä- ja alarivillä.
LEVEYS, KORKEUS = 26, 32
RAM_SARAKKEET = (6, 19)


def paikat(sij: dict[str, Any]) -> dict[str, list[tuple[int, int, int]]]:
    """Solutyypeittäin (x, y, z) nextpnr:n kirjoittamasta sijoittelusta."""
    tulos: dict[str, list[tuple[int, int, int]]] = {}
    moduuli = next(iter(sij["modules"].values()))
    for solu in moduuli["cells"].values():
        bel = solu.get("attributes", {}).get("NEXTPNR_BEL")
        if not bel:
            continue
        x, y, nimi = bel.split("/")
        z = int(nimi[2:]) if nimi.startswith("lc") else 0
        tulos.setdefault(solu["type"], []).append((int(x[1:]), int(y[1:]), z))
    return tulos


def piirra_sijoittelu(ax: Any, sij: dict[str, Any], pnr: dict[str, Any],
                      otsikko: str) -> None:
    for x in range(1, LEVEYS - 1):
        for y in range(1, KORKEUS - 1):
            vari = "#EEF1F2" if x in RAM_SARAKKEET else "white"
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=vari,
                                   edgecolor=VAALEA, lw=0.3))
    p = paikat(sij)
    for x, y, z in p.get("ICESTORM_LC", []):
        ax.add_patch(Rectangle((x + 0.08, y + z / 8), 0.84, 1 / 8,
                               facecolor=KOROSTUS, edgecolor="none"))
    for x, y, _ in p.get("SB_IO", []):
        ax.add_patch(Rectangle((x + 0.15, y + 0.15), 0.7, 0.7,
                               facecolor=TOINEN, edgecolor="none"))
    for x, y, _ in p.get("ICESTORM_PLL", []):
        ax.add_patch(Rectangle((x - 0.5, y + 0.1), 2.0, 0.8,
                               facecolor=KOLMAS, edgecolor="none"))
    # Kriittinen polku solujen sijaintien kautta.
    xs: list[float] = []
    ys: list[float] = []
    for osa in kriittinen(pnr):
        for paa in ("from", "to"):
            lx, ly = osa[paa]["loc"]
            if not xs or (xs[-1], ys[-1]) != (lx + 0.5, ly + 0.5):
                xs.append(lx + 0.5)
                ys.append(ly + 0.5)
    ax.plot(xs, ys, color="#1F2A2E", lw=1.1, marker="o", ms=2.2)
    ax.set_xlim(0, LEVEYS)
    ax.set_ylim(0, KORKEUS)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color(HARMAA)
    ax.set_title(otsikko, fontsize=9)


def selite(fig: Any, pll: bool) -> None:
    kahvat = [Rectangle((0, 0), 1, 1, color=KOROSTUS),
              Rectangle((0, 0), 1, 1, color=TOINEN),
              Line2D([0], [0], color="#1F2A2E", lw=1.1, marker="o",
                     ms=2.2)]
    nimet = ["logiikkasolu", "IO-solu", "kriittinen polku"]
    if pll:
        kahvat.insert(2, Rectangle((0, 0), 1, 1, color=KOLMAS))
        nimet.insert(2, "PLL")
    fig.legend(kahvat, nimet, ncol=2 if pll else 3, frameon=False,
               loc="lower center", fontsize=8, bbox_to_anchor=(0.5, -0.03))


def sijoittelut(r: Path, kohde: Path) -> None:
    """Esittelysuunnitelman sijoittelu ja kertojan kaksi siementä."""
    pnr = lue(r / "kortti.pnr.json")
    fig, ax = plt.subplots(figsize=(3.6, 4.4))
    lc = pnr["utilization"]["ICESTORM_LC"]["used"]
    piirra_sijoittelu(ax, lue(r / "kortti.sij.json"), pnr,
                      f"esittelysuunnitelma: {lc} solua, "
                      f"{fmax(pnr):.0f} MHz")
    selite(fig, pll=True)
    fig.savefig(kohde / "sijoittelu.png")
    plt.close(fig)

    tulokset = {s: fmax(lue(r / f"siemen-{s}.pnr.json")) for s in range(1, 6)}
    hitain = min(tulokset, key=lambda s: tulokset[s])
    nopein = max(tulokset, key=lambda s: tulokset[s])
    fig, akselit = plt.subplots(1, 2, figsize=(7.0, 4.4))
    for ax, s in zip(akselit, (hitain, nopein)):
        mhz = f"{tulokset[s]:.1f}".replace(".", ",")
        piirra_sijoittelu(ax, lue(r / f"siemen-{s}.sij.json"),
                          lue(r / f"siemen-{s}.pnr.json"),
                          f"siemen {s}: {mhz} MHz")
    selite(fig, pll=False)
    fig.subplots_adjust(wspace=0.05)
    fig.savefig(kohde / "siemenet.png")
    plt.close(fig)


# --- Yosysin piirikaaviot --------------------------------------------------

def piirikaaviot(r: Path, kohde: Path) -> None:
    """Yosysin show-komennon dot-tiedostot PNG-kuviksi Graphvizilla."""
    for nimi in ("vilkku-rtl", "vilkku-portit"):
        subprocess.run(["dot", "-Tpng", "-Gdpi=100", "-Nfontname=DejaVu Sans",
                        "-Efontname=DejaVu Sans", str(r / f"{nimi}.dot"),
                        "-o", str(kohde / f"{nimi}.png")], check=True)


def main() -> None:
    r, kohde = Path(sys.argv[1]), Path(sys.argv[2])
    kohde.mkdir(parents=True, exist_ok=True)
    kehykset(r, kohde)
    resurssit(r, kohde)
    polut(r, kohde)
    sijoittelut(r, kohde)
    piirikaaviot(r, kohde)


if __name__ == "__main__":
    main()
