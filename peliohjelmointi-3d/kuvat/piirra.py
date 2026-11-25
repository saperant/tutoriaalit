"""Tuottaa paketin kuvat esimerkkiohjelmista.

Käyttö: python3 kuvat/piirra.py   (ajetaan komennolla `make kuvat`)

Skripti kääntää esimerkit väliaikaiseen hakemistoon ja ajaa ne
kuvitustilassa: kun esimerkille annetaan argumentiksi tiedoston nimi, se
tallentaa oman ohjelmistorenderöijänsä kuvan (PPM) ja osa myös
reittinsä tekstinä. Ohjelman testattu tuloste on sama molemmissa
tiloissa. Kuvat ovat versionhallinnassa.
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
from matplotlib.patches import Polygon

KOROSTUS = "#4552B0"
PUNAINEN = "#B04848"
KELTAINEN = "#C89B1E"
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
    polku = ESIM / nimi
    lahteet = (sorted(polku.glob("*.cpp")) if polku.is_dir()
               else [polku.with_suffix(".cpp")])
    binaari = tyo / nimi
    subprocess.run([KAANTAJA, "-std=c++23", "-O2", "-DKUVAN_SUURENNOS=2",
                    *map(str, lahteet), "-o", str(binaari)], check=True)
    syote = ESIM / f"{nimi}.syote"
    return subprocess.run(
        [str(binaari), *argumentit], capture_output=True, text=True,
        check=True, cwd=tyo,
        input=syote.read_text("utf-8") if syote.exists() else "").stdout


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
    vali = 16
    kangas = np.full((rivit * h + (rivit - 1) * vali,
                      sarakkeita * w + (sarakkeita - 1) * vali, 3), 255,
                     dtype=np.uint8)
    for i, kuva in enumerate(kuvat):
        y, x = (i // sarakkeita) * (h + vali), (i % sarakkeita) * (w + vali)
        kangas[y:y + h, x:x + w] = kuva
    plt.imsave(KUVAT / f"{nimi}.png", kangas)


def rata(tyo: Path) -> None:
    """Hahmon reitti sivusta: korkeus matkan funktiona ja tila väreinä."""
    data = np.loadtxt(tyo / "rata.txt")
    x, y, maassa = data[:, 0], data[:, 1], data[:, 3] > 0
    fig, ax = plt.subplots(figsize=(7.2, 2.0))
    # Radan profiili z = 0 kohdalla (samat mitat kuin esimerkissä).
    profiili = [(4, 0), (8, 1.5), (12, 1.5), (12, 0), (16, 0), (17.5, 3),
                (17.5, 0), (23, 0)]
    for i in range(5):
        profiili += [(23 + 0.4 * i, 0.25 * (i + 1)),
                     (23.4 + 0.4 * i, 0.25 * (i + 1))]
    profiili += [(28, 1.25), (28, 0)]
    px, py = zip(*profiili)
    ax.fill_between(px, py, color=VAALEA, step=None, linewidth=0)
    ax.plot(px, py, color=HARMAA, linewidth=0.8)
    ax.scatter(x[maassa], y[maassa], s=2, color=KOROSTUS, label="maassa")
    ax.scatter(x[~maassa], y[~maassa], s=2, color=KELTAINEN,
               label="ilmassa")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("jalkojen korkeus (m)")
    ax.set_xlim(0, 36)
    ax.set_ylim(-0.1, 3.2)
    ax.legend(loc="upper right", frameon=False, markerscale=4)
    fig.savefig(KUVAT / "rata-profiili.png")
    plt.close(fig)


def karsinta(tyo: Path) -> None:
    """Kenttä ylhäältä: näkymäkartio ja pallot karsinnan mukaan."""
    data = np.loadtxt(tyo / "karsinta.txt")
    x, z, nakyy = data[:, 0], data[:, 1], data[:, 3] > 0
    fig, ax = plt.subplots(figsize=(4.4, 4.4))
    ax.scatter(x[~nakyy], z[~nakyy], s=4, color=VAALEA, label="karsittu")
    ax.scatter(x[nakyy], z[nakyy], s=6, color=KOROSTUS, label="näkyvissä")
    # Kartion pohjapiirros: kääntö 45 astetta, vaakakulma pystykulmasta
    # 60 astetta ja kuvasuhteesta 16:9, kaukotaso 60 m.
    puolikulma = np.arctan(np.tan(np.radians(30)) * 16 / 9)
    kaanto = np.radians(45)
    kulmat = []
    for merkki in (-1, 1):
        suunta = kaanto + merkki * puolikulma
        pituus = 60 / np.cos(puolikulma)
        kulmat.append((-np.sin(suunta) * pituus, -np.cos(suunta) * pituus))
    ax.add_patch(Polygon([(0, 0), *kulmat], closed=True, fill=False,
                         edgecolor=PUNAINEN, linewidth=1.2))
    ax.plot(0, 0, marker="o", color=PUNAINEN, markersize=4)
    ax.set_xlim(-100, 100)
    ax.set_ylim(100, -100)  # -z ylöspäin: kameran oletussuunta
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("z (m)")
    ax.legend(loc="lower right", frameon=False, markerscale=2)
    fig.savefig(KUVAT / "karsinta-ylhaalta.png")
    plt.close(fig)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tyo = Path(tmp)
        aja(tyo, "01-kohtaus", "kohtaus.ppm")
        tallenna("kohtaus", [lue_ppm(tyo / "kohtaus.ppm")])
        aja(tyo, "03-slerp", "slerp.ppm")
        tallenna("slerp", [lue_ppm(tyo / "slerp.ppm")])
        aja(tyo, "04-hierarkia", "nosturi")
        tallenna("nosturi", [lue_ppm(tyo / f"nosturi-{i}.ppm")
                             for i in (1, 2)])
        aja(tyo, "05-muodot", "muodot.ppm")
        tallenna("muodot", [lue_ppm(tyo / "muodot.ppm")])
        aja(tyo, "06-sateet", "sateet.ppm")
        tallenna("sateet", [lue_ppm(tyo / "sateet.ppm")])
        aja(tyo, "07-bvh", "bvh.ppm")
        tallenna("bvh", [lue_ppm(tyo / "bvh.ppm")])
        aja(tyo, "08-seuranta", "kamera")
        tallenna("kamera", [lue_ppm(tyo / f"kamera-{i}.ppm")
                            for i in (1, 2)])
        aja(tyo, "09-hahmo", "rata")
        tallenna("rata", [lue_ppm(tyo / "rata.ppm")])
        rata(tyo)
        aja(tyo, "10-karsinta", "karsinta")
        tallenna("karsinta", [lue_ppm(tyo / "karsinta.ppm")])
        karsinta(tyo)
        aja(tyo, "11-luuranko", "skinnaus")
        tallenna("skinnaus", [lue_ppm(tyo / f"skinnaus-{i}.ppm")
                              for i in (1, 2, 3)])
        aja(tyo, "13-lyhty", "lyhty")
        tallenna("lyhty", [lue_ppm(tyo / f"lyhty-{i}.ppm")
                           for i in (1, 2, 3, 4, 5, 6)], sarakkeita=3)


if __name__ == "__main__":
    main()
