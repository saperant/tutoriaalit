"""Tuottaa paketin kuvat esimerkkiohjelmista.

Käyttö: python3 kuvat/piirra.py   (ajetaan komennolla `make kuvat`)

Skripti kääntää esimerkit väliaikaiseen hakemistoon ja ajaa ne
kuvitustilassa: kun esimerkille annetaan argumentiksi nimi, se
tallentaa oman ohjelmistorenderöijänsä kuvia (PPM) ja aikasarjoja
tekstinä. Ohjelman testattu tuloste on sama molemmissa tiloissa.
Kaksi kuvaa (Minkowskin erotus ja kitkakartio) ovat periaatekuvia,
jotka lasketaan tässä skriptissä. Kuvat ovat versionhallinnassa.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Circle, Polygon, Rectangle

KOROSTUS = "#4552B0"
PUNAINEN = "#B04848"
KELTAINEN = "#C89B1E"
VIHREA = "#4E8A5A"
HARMAA = "#5B6B70"
VAALEA = "#C9D2D6"
FONTIT = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({"font.family": "Inter" if "Inter" in FONTIT
                     else "DejaVu Sans",
                     "font.size": 9, "figure.dpi": 100, "savefig.dpi": 200,
                     "savefig.bbox": "tight", "axes.spines.top": False,
                     "axes.spines.right": False})

JUURI = Path(__file__).resolve().parent.parent
ESIM = JUURI / "esimerkit"
KUVAT = JUURI / "kuvat"
KAANTAJA = shutil.which("g++-14") or "g++"


def aja(tyo: Path, nimi: str, *argumentit: str) -> str:
    """Kääntää esimerkin (-O2) ja ajaa sen työhakemistossa."""
    binaari = tyo / nimi
    subprocess.run([KAANTAJA, "-std=c++23", "-O2", "-DKUVAN_SUURENNOS=2",
                    str(ESIM / f"{nimi}.cpp"), "-o", str(binaari)],
                   check=True)
    return subprocess.run([str(binaari), *argumentit], capture_output=True,
                          text=True, check=True, cwd=tyo).stdout


def lue_ppm(polku: Path) -> np.ndarray:
    data = polku.read_bytes()
    osat = data.split(maxsplit=4)
    leveys, korkeus = int(osat[1]), int(osat[2])
    return np.frombuffer(osat[4][:leveys * korkeus * 3],
                         dtype=np.uint8).reshape(korkeus, leveys, 3)


def tallenna(nimi: str, kuvat: list[np.ndarray], sarakkeita: int = 0) -> None:
    """Tallentaa kuvan tai usean kuvan ruudukon valkoisin välein."""
    sarakkeita = sarakkeita or len(kuvat)
    h, w, _ = kuvat[0].shape
    rivit = -(-len(kuvat) // sarakkeita)
    vali = 12
    kangas = np.full((rivit * h + (rivit - 1) * vali,
                      sarakkeita * w + (sarakkeita - 1) * vali, 3), 255,
                     dtype=np.uint8)
    for i, kuva in enumerate(kuvat):
        y, x = (i // sarakkeita) * (h + vali), (i % sarakkeita) * (w + vali)
        kangas[y:y + h, x:x + w] = kuva
    plt.imsave(KUVAT / f"{nimi}.png", kangas)


def sarja(tyo: Path, nimi: str, maara: int) -> list[np.ndarray]:
    return [lue_ppm(tyo / f"{nimi}-{i}.ppm") for i in range(1, maara + 1)]


def integrointi(tyo: Path) -> None:
    """Vapaa pyöriminen neljällä tavalla: energia ja liikemäärämomentti."""
    data = np.loadtxt(tyo / "kirja.txt")
    nimet = ["vakio ω", "eksplisiittinen", "L säilyy", "L ja keskipiste"]
    varit = [HARMAA, PUNAINEN, KELTAINEN, KOROSTUS]
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.4, 2.3))
    for tapa in range(4):
        d = data[data[:, 0] == tapa]
        a.plot(d[:, 1], d[:, 2], color=varit[tapa], label=nimet[tapa])
        b.plot(d[:, 1], d[:, 3], color=varit[tapa])
    d = data[data[:, 0] == 3]
    c.plot(d[:, 1], d[:, 4], color=KOROSTUS)
    a.set_ylabel("E / E₀")
    b.set_ylabel("|L − L₀| / L₀")
    c.set_ylabel("akselin suunta (z)")
    for ax in (a, b, c):
        ax.set_xlabel("aika (s)")
    a.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(KUVAT / "integrointi.png")
    plt.close(fig)


def kitka(tyo: Path) -> None:
    data = np.loadtxt(tyo / "kitka.txt")
    fig, ax = plt.subplots(figsize=(4.6, 2.2))
    ax.plot(data[:, 0], data[:, 1], color=KOROSTUS, label="etenemisnopeus v")
    ax.plot(data[:, 0], data[:, 2], color=KELTAINEN,
            label="kehänopeus ω r")
    ax.axhline(5, color=HARMAA, linewidth=0.6, linestyle=":")
    ax.text(0.98, 5.12, "5/7 v₀", color=HARMAA, ha="right", fontsize=8)
    ax.set_xlabel("aika (s)")
    ax.set_ylabel("m/s")
    ax.legend(frameon=False, loc="center right")
    fig.savefig(KUVAT / "kitka.png")
    plt.close(fig)


def kitkakartio() -> None:
    """Periaatekuva: kitkakartion poikkileikkaus ja sen likiarvot."""
    fig, ax = plt.subplots(figsize=(2.9, 2.9))
    ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor=KOROSTUS,
                        linewidth=1.5, label="kartio"))
    ax.add_patch(Rectangle((-1, -1), 2, 2, fill=False, edgecolor=PUNAINEN,
                           linewidth=1.2, label="kaksi akselia erikseen"))
    k = np.sqrt(0.5)
    ax.add_patch(Rectangle((-k, -k), 2 * k, 2 * k, fill=False,
                           edgecolor=VIHREA, linewidth=1.0, linestyle="--",
                           label="sisään piirretty"))
    ax.annotate("", xy=(1, 1), xytext=(0, 0),
                arrowprops={"arrowstyle": "->", "color": PUNAINEN})
    ax.text(1.06, 1.05, "√2 μN", color=PUNAINEN, fontsize=8)
    ax.annotate("", xy=(1, 0), xytext=(0, 0),
                arrowprops={"arrowstyle": "->", "color": KOROSTUS})
    ax.text(0.5, -0.17, "μN", color=KOROSTUS, fontsize=8)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.9)
    ax.set_aspect("equal")
    ax.set_xlabel("kitka suunnassa t₁")
    ax.set_ylabel("kitka suunnassa t₂")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(frameon=False, fontsize=7, loc="upper center", ncol=1)
    fig.savefig(KUVAT / "kitkakartio.png")
    plt.close(fig)


def ratkaisija(tyo: Path) -> None:
    nimet = ["4 kierrosta, kylmä", "10 kierrosta, kylmä",
             "4 kierrosta, lämmin", "10 kierrosta, lämmin"]
    varit = [PUNAINEN, KELTAINEN, VIHREA, KOROSTUS]
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    for i in range(4):
        d = np.loadtxt(tyo / f"pino-{i + 1}.txt")
        ax.plot(d[:, 0], d[:, 1], color=varit[i], label=nimet[i])
    ax.axhline(5.5, color=HARMAA, linewidth=0.6, linestyle=":")
    ax.set_xlabel("aika (s)")
    ax.set_ylabel("ylimmän laatikon korkeus (m)")
    ax.set_ylim(4.2, 5.6)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    fig.savefig(KUVAT / "ratkaisija.png")
    plt.close(fig)


def nopea(tyo: Path) -> None:
    data = np.loadtxt(tyo / "nopea.txt")
    fig, ax = plt.subplots(figsize=(5.2, 2.2))
    ax.axhspan(4.95, 5.05, color=HARMAA, alpha=0.5, linewidth=0)
    ax.text(0.5, 5.25, "seinä", color=HARMAA, fontsize=8)
    for jatkuva, vari, nimi in ((0, PUNAINEN, "diskreetti"),
                                (1, KOROSTUS, "jatkuva")):
        d = data[(data[:, 0] == jatkuva) & (data[:, 1] <= 16)]
        ax.plot(d[:, 1], d[:, 2], marker="o", markersize=3, color=vari,
                label=nimi)
    ax.set_xlabel("askel")
    ax.set_ylabel("pallon paikka x (m)")
    ax.legend(frameon=False, loc="upper left")
    fig.savefig(KUVAT / "nopea.png")
    plt.close(fig)


def minkowski() -> None:
    """Periaatekuva: kahden kuperan monikulmion Minkowskin erotus."""
    def erotus(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        pisteet = np.array([p - q for p in a for q in b])
        keski = pisteet.mean(axis=0)
        # Kupera verho: lajittelu kulman mukaan riittää, koska piirretään
        # vain ulkoreunan pisteet (monotoninen ketju).
        pisteet = pisteet[np.lexsort((pisteet[:, 1], pisteet[:, 0]))]

        def risti(o: np.ndarray, p: np.ndarray, q: np.ndarray) -> float:
            return float((p[0] - o[0]) * (q[1] - o[1]) -
                         (p[1] - o[1]) * (q[0] - o[0]))
        ala: list[np.ndarray] = []
        for p in pisteet:
            while len(ala) >= 2 and risti(ala[-2], ala[-1], p) <= 0:
                ala.pop()
            ala.append(p)
        yla: list[np.ndarray] = []
        for p in pisteet[::-1]:
            while len(yla) >= 2 and risti(yla[-2], yla[-1], p) <= 0:
                yla.pop()
            yla.append(p)
        del keski
        return np.array(ala[:-1] + yla[:-1])

    kolmio = np.array([(0.0, 0.0), (1.6, 0.2), (0.6, 1.4)])
    nelio = np.array([(0.0, 0.0), (1.2, 0.0), (1.2, 1.0), (0.0, 1.0)])
    fig, akselit = plt.subplots(2, 2, figsize=(6.0, 4.4))
    for rivi, siirto, otsikko in ((0, np.array([2.2, 0.3]), "erillään"),
                                  (1, np.array([1.0, 0.4]), "sisäkkäin")):
        b = nelio + siirto
        vas, oik = akselit[rivi]
        vas.add_patch(Polygon(kolmio, closed=True, facecolor=KOROSTUS,
                              alpha=0.5, edgecolor=KOROSTUS))
        vas.add_patch(Polygon(b, closed=True, facecolor=KELTAINEN,
                              alpha=0.5, edgecolor=KELTAINEN))
        vas.set_title(f"muodot A ja B {otsikko}", fontsize=8)
        vas.set_xlim(-0.5, 3.8)
        vas.set_ylim(-0.4, 1.8)
        d = erotus(kolmio, b)
        oik.add_patch(Polygon(d, closed=True, facecolor=VAALEA,
                              edgecolor=HARMAA))
        oik.plot(0, 0, marker="+", color=PUNAINEN, markersize=10,
                 markeredgewidth=1.5)
        oik.set_title("erotus A − B ja origo", fontsize=8)
        oik.set_xlim(-3.8, 1.2)
        oik.set_ylim(-1.8, 1.4)
        for ax in (vas, oik):
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
            for reuna in ax.spines.values():
                reuna.set_visible(False)
    fig.tight_layout()
    fig.savefig(KUVAT / "minkowski.png")
    plt.close(fig)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tyo = Path(tmp)
        aja(tyo, "01-ensimmainen", "eka")
        tallenna("ensimmainen", sarja(tyo, "eka", 6), sarakkeita=3)
        aja(tyo, "03-integrointi", "kirja")
        tallenna("kaanto", sarja(tyo, "kirja", 10), sarakkeita=5)
        integrointi(tyo)
        aja(tyo, "04-kosketus", "kosketus.ppm")
        tallenna("kosketus", [lue_ppm(tyo / "kosketus.ppm")])
        aja(tyo, "05-tormays", "tormays")
        tallenna("tormays", sarja(tyo, "tormays", 4))
        aja(tyo, "06-kitka", "kitka.txt")
        kitka(tyo)
        kitkakartio()
        aja(tyo, "07-ratkaisija", "pino")
        ratkaisija(tyo)
        aja(tyo, "08-nivelet", "ketju")
        tallenna("ketju", sarja(tyo, "ketju", 6))
        aja(tyo, "09-pino", "pyramidi")
        tallenna("pyramidi", sarja(tyo, "pyramidi", 6), sarakkeita=3)
        aja(tyo, "10-nopea", "nopea.txt")
        nopea(tyo)
        aja(tyo, "11-kangas", "kangas")
        tallenna("kangas", sarja(tyo, "kangas", 4))
        aja(tyo, "12-vesi", "vesi")
        tallenna("vesi", sarja(tyo, "vesi", 4), sarakkeita=2)
        minkowski()


if __name__ == "__main__":
    main()
