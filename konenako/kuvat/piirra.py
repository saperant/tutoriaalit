"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvat lasketaan
ajamalla testatut esimerkit ja lukemalla niiden muuttujat, joten kuva
näyttää täsmälleen sen, minkä esimerkki laskee.
"""

import contextlib
import io
import runpy
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"


def aja(nimi: str) -> dict[str, Any]:
    """Ajaa esimerkin hiljaa ja palauttaa sen globaalit muuttujat."""
    polku = ESIMERKIT / nimi
    sys.path.insert(0, str(polku.parent))
    with contextlib.redirect_stdout(io.StringIO()):
        tulos = runpy.run_path(str(polku))
    sys.path.pop(0)
    return tulos


def nimioi(kuva: np.ndarray, teksti: str) -> np.ndarray:
    """Harmaa kuva värikuvaksi ja nimiö vasempaan yläkulmaan."""
    vari = kuva if kuva.ndim == 3 else cv2.cvtColor(kuva, cv2.COLOR_GRAY2BGR)
    vari = vari.copy()
    cv2.rectangle(vari, (0, 0), (8 + 9 * len(teksti), 22), (255, 255, 255),
                  -1)
    cv2.putText(vari, teksti, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 0, 0), 1, cv2.LINE_AA)
    return vari


def rivi(kuvat: list[np.ndarray], vali: int = 6) -> np.ndarray:
    korkeus = max(k.shape[0] for k in kuvat)
    osat = []
    for k in kuvat:
        k = cv2.copyMakeBorder(k, 0, korkeus - k.shape[0], 0, vali,
                               cv2.BORDER_CONSTANT, value=(255, 255, 255))
        osat.append(k)
    return np.hstack(osat)[:, :-vali]


def tallenna(polku: Path, kuva: np.ndarray) -> None:
    cv2.imwrite(str(polku), kuva, [cv2.IMWRITE_PNG_COMPRESSION, 9])


def kynnystys(kohde: Path) -> None:
    g = aja("02-kynnystys.py")
    tallenna(kohde / "kynnystys.png", rivi([
        nimioi(g["kuva"], "kuva"), nimioi(g["otsu"], "Otsu"),
        nimioi(g["adaptiivinen"], "adaptiivinen")]))


def kohina(kohde: Path) -> None:
    g = aja("03-kohina.py")
    s = g["suola"]
    tallenna(kohde / "kohina.png", rivi([
        nimioi(s, "suola ja pippuri"),
        nimioi(cv2.GaussianBlur(s, (5, 5), 0), "Gauss 5x5"),
        nimioi(cv2.medianBlur(s, 5), "mediaani 5")]))


def sovitus(kohde: Path) -> None:
    g = aja("05-sovitus.py")
    a, b = g["nakyma"], g["toinen"]
    orb = cv2.ORB.create(nfeatures=1000)
    kp1, d1 = orb.detectAndCompute(a, None)
    kp2, d2 = orb.detectAndCompute(b, None)
    parit = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(d1, d2, k=2)
    hyvat = [p[0] for p in parit
             if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
    hyvat = sorted(hyvat, key=lambda m: m.distance)[:40]
    kuva = cv2.drawMatches(a, kp1, b, kp2, hyvat, None,
                           matchColor=(40, 140, 40),
                           flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    tallenna(kohde / "sovitus.png", cv2.resize(kuva, None, fx=0.75, fy=0.75,
                                               interpolation=cv2.INTER_AREA))


def kalibrointi(kohde: Path) -> None:
    g = aja("07-kalibrointi/main.py")
    kuva = cv2.cvtColor(g["kuva"], cv2.COLOR_GRAY2BGR)
    cv2.drawChessboardCorners(kuva, g["kuvio"], g["kulmat"], True)
    tallenna(kohde / "kalibrointi.png",
             cv2.resize(kuva, None, fx=0.6, fy=0.6,
                        interpolation=cv2.INTER_AREA))


def stereo(kohde: Path) -> None:
    g = aja("08-stereo.py")
    d = np.clip(g["dispariteetti"], 0, 32) * (255 / 32)
    varikartta = cv2.applyColorMap(d.astype(np.uint8), cv2.COLORMAP_VIRIDIS)
    tallenna(kohde / "stereo.png", rivi([
        nimioi(g["vasen"], "vasen"), nimioi(g["oikea"], "oikea"),
        nimioi(varikartta, "dispariteetti")]))


def watershed(kohde: Path) -> None:
    g = aja("09-watershed.py")
    nimiot = g["tulos"]
    vari = np.full((*nimiot.shape, 3), 255, np.uint8)
    paletti = [(180, 119, 31), (14, 127, 255), (44, 160, 44),
               (40, 39, 214), (189, 103, 148), (75, 86, 140)]
    for i, k in enumerate(g["alueet"]):
        vari[nimiot == k] = paletti[i % len(paletti)]
    vari[nimiot == -1] = (0, 0, 0)
    tallenna(kohde / "watershed.png", rivi([
        nimioi(g["maski"], "maski"),
        nimioi(cv2.normalize(g["etaisyys"], None, 0, 255,
                             cv2.NORM_MINMAX).astype(np.uint8),
               "etaisyys"),
        nimioi(vari, "watershed")]))


if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    for piirra in (kynnystys, kohina, sovitus, kalibrointi, stereo,
                   watershed):
        piirra(kohde)
