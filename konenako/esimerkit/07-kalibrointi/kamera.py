"""Synteettinen kamera: shakkilaudan kuva tunnetulla kameramallilla.

Kuva renderöidään säteenseurannan tapaan takaperin: jokaiselle
kuvapikselille lasketaan vääristymätön suunta, säde leikataan laudan
tasolla ja väri luetaan laudan tekstuurista. Kuva lasketaan kaksinkertaisella
tarkkuudella ja pienennetään, jolloin reunat ovat pehmeät kuten oikeassa
kamerassa.
"""

import functools
from dataclasses import dataclass

import cv2
import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]


# @alku malli
@dataclass(frozen=True)
class Kamera:
    """Neulanreikäkamera ja Brownin–Conradyn vääristymämalli."""

    fx: float = 800.0
    fy: float = 800.0
    cx: float = 320.0
    cy: float = 240.0
    k1: float = -0.25          # säteittäinen vääristymä (tynnyri < 0)
    k2: float = 0.08
    leveys: int = 640
    korkeus: int = 480

    def K(self) -> Taulukko:
        return np.array([[self.fx, 0.0, self.cx],
                         [0.0, self.fy, self.cy],
                         [0.0, 0.0, 1.0]])

    def vaaristyma(self) -> Taulukko:
        return np.array([self.k1, self.k2, 0.0, 0.0, 0.0])
# @loppu malli


@dataclass(frozen=True)
class Lauta:
    """Shakkilauta: sisäkulmat sarakkeet x rivit, ruutu millimetreinä."""

    sarakkeet: int = 9
    rivit: int = 6
    ruutu: float = 25.0

    def kulmat(self) -> Taulukko:
        """Sisäkulmat laudan koordinaatistossa (Z = 0), rivi kerrallaan."""
        j, i = np.mgrid[0:self.rivit, 0:self.sarakkeet]
        xy = np.stack([(i + 1) * self.ruutu, (j + 1) * self.ruutu], -1)
        return np.hstack([xy.reshape(-1, 2), np.zeros((xy.size // 2, 1))])

    def vari(self, x: Taulukko, y: Taulukko) -> Taulukko:
        """Laudan harmaasävy kohdassa (x, y) mm; reunuksena valkoinen."""
        sx = np.floor(x / self.ruutu)
        sy = np.floor(y / self.ruutu)
        sisalla = ((sx >= 0) & (sx <= self.sarakkeet)
                   & (sy >= 0) & (sy <= self.rivit))
        musta = sisalla & ((sx + sy) % 2 == 0)
        return np.where(musta, 30.0, 220.0)


# @alku render
@functools.cache
def suunnat(kamera: Kamera, kerroin: int) -> Taulukko:
    """Jokaisen ylinäytteistetyn pikselin vääristymätön suunta (x, y).

    Kaikki kuvat käyttävät samaa kameraa, joten taulukko lasketaan kerran.
    """
    w, h = kamera.leveys * kerroin, kamera.korkeus * kerroin
    # Ylinäytteistetyn pikselin keskikohta alkuperäisessä kuvassa.
    v, u = np.mgrid[0:h, 0:w]
    pisteet = np.stack([(u + 0.5) / kerroin - 0.5,
                        (v + 0.5) / kerroin - 0.5], -1).reshape(-1, 1, 2)
    # Vääristyneestä pikselistä vääristymättömään normalisoituun suuntaan.
    ehto = (cv2.TERM_CRITERIA_COUNT + cv2.TERM_CRITERIA_EPS, 50, 1e-12)
    tulos = cv2.undistortPoints(pisteet.astype(np.float64), kamera.K(),
                                kamera.vaaristyma(), criteria=ehto)
    return np.asarray(tulos, np.float64).reshape(-1, 2)


def renderoi(kamera: Kamera, lauta: Lauta, rvec: Taulukko,
             tvec: Taulukko, kerroin: int = 4) -> npt.NDArray[np.uint8]:
    """Kuva laudasta asennossa (rvec, tvec); kerroin = ylinäytteistys."""
    suunta = suunnat(kamera, kerroin)
    # Laudan taso kameran koordinaatistossa: X_c = R X_l + t, Z_l = 0, eli
    # (x, y, 1) ~ [r1 r2 t] (X, Y, 1). Ratkaistaan (X, Y) käänteisellä.
    R, _ = cv2.Rodrigues(rvec)
    H = np.column_stack([R[:, 0], R[:, 1], tvec.ravel()])
    laudalla = np.linalg.solve(H, np.column_stack(
        [suunta, np.ones(len(suunta))]).T)
    x, y = laudalla[0] / laudalla[2], laudalla[1] / laudalla[2]
    w, h = kamera.leveys * kerroin, kamera.korkeus * kerroin
    kuva = lauta.vari(x, y).reshape(h, w).astype(np.float32)
    pieni = cv2.resize(kuva, (kamera.leveys, kamera.korkeus),
                       interpolation=cv2.INTER_AREA)
    return np.clip(np.round(pieni), 0, 255).astype(np.uint8)
# @loppu render


def asennot() -> list[tuple[Taulukko, Taulukko]]:
    """Kymmenen erilaista laudan asentoa (kierto, siirto millimetreinä)."""
    tulos = []
    for i in range(10):
        # Kiertovektori: suunta on kiertoakseli, pituus kulma radiaaneina.
        rvec = np.radians([18.0 * np.sin(i), 22.0 * np.cos(1.7 * i),
                           8.0 * np.sin(2.3 * i)]).reshape(3, 1)
        siirto = np.array([-125.0 + 25 * np.sin(1.3 * i),
                           -85.0 + 20 * np.cos(0.9 * i),
                           520.0 + 60 * np.sin(0.7 * i)])
        tulos.append((rvec.astype(np.float64), siirto.reshape(3, 1)))
    return tulos
