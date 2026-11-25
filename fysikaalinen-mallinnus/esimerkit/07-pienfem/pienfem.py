"""pienfem: pieni elementtikirjasto lineaarisille kolmioille.

Kirjasto on kirjoitettu luettavaksi, ei nopeaksi: kokoaminen on
silmukka elementtien yli. Myöhemmät esimerkit käyttävät tätä ja
vertaavat sitä scikit-fem-kirjastoon."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

Taulukko = npt.NDArray[np.float64]
Indeksit = npt.NDArray[np.int64]
Funktio = Callable[[Taulukko, Taulukko], Taulukko]


# @alku verkko
@dataclass(frozen=True)
class Verkko:
    """Kolmioverkko: solmujen koordinaatit ja kolmioiden solmunumerot."""
    pisteet: Taulukko          # muoto (solmuja, 2)
    kolmiot: Indeksit          # muoto (kolmioita, 3), vastapäivään

    def reunasarmat(self) -> Indeksit:
        """Särmät, jotka kuuluvat vain yhteen kolmioon: alueen reuna."""
        sarmat = np.concatenate([self.kolmiot[:, [0, 1]],
                                 self.kolmiot[:, [1, 2]],
                                 self.kolmiot[:, [2, 0]]])
        avain = np.sort(sarmat, axis=1)
        _, eka, maara = np.unique(avain, axis=0, return_index=True,
                                  return_counts=True)
        tulos: Indeksit = sarmat[eka[maara == 1]]
        return tulos

    def reunasolmut(self) -> Indeksit:
        tulos: Indeksit = np.unique(self.reunasarmat())
        return tulos


def suorakulmio(nx: int, ny: int, leveys: float = 1.0,
                korkeus: float = 1.0) -> Verkko:
    """nx x ny ruutua, kukin jaettu lävistäjällä kahdeksi kolmioksi."""
    x, y = np.meshgrid(np.linspace(0.0, leveys, nx + 1),
                       np.linspace(0.0, korkeus, ny + 1))
    pisteet = np.column_stack([x.ravel(), y.ravel()])
    kolmiot = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i              # ruudun vasen alakulma
            b, c, d = a + 1, a + nx + 2, a + nx + 1
            kolmiot += [[a, b, c], [a, c, d]]
    return Verkko(pisteet, np.array(kolmiot, dtype=np.int64))
# @loppu verkko


def l_alue(n: int) -> Verkko:
    """L-kirjain: neliö [-1, 1]² ilman neljännestä x > 0, y < 0."""
    koko = suorakulmio(2 * n, 2 * n, 2.0, 2.0)
    pisteet = koko.pisteet - 1.0
    keski = pisteet[koko.kolmiot].mean(axis=1)
    mukana = ~((keski[:, 0] > 0.0) & (keski[:, 1] < 0.0))
    kolmiot = koko.kolmiot[mukana]
    kaytossa, uudet = np.unique(kolmiot, return_inverse=True)
    return Verkko(pisteet[kaytossa],
                  uudet.reshape(-1, 3).astype(np.int64))


# @alku elementti
def elementti(p: Taulukko) -> tuple[Taulukko, float]:
    """Kolmion kantafunktioiden gradientit (3 x 2) ja pinta-ala.

    Kantafunktio i on 1 solmussa i ja 0 kahdessa muussa. Sen gradientti
    on vakio ja kohtisuorassa vastakkaista sivua vastaan."""
    b = np.array([p[1, 1] - p[2, 1], p[2, 1] - p[0, 1], p[0, 1] - p[1, 1]])
    c = np.array([p[2, 0] - p[1, 0], p[0, 0] - p[2, 0], p[1, 0] - p[0, 0]])
    ala = 0.5 * (b[0] * c[1] - b[1] * c[0])
    if ala <= 0.0:
        raise ValueError("kolmion solmut eivät ole vastapäivään")
    return np.column_stack([b, c]) / (2.0 * ala), float(ala)


def elementtimatriisi(p: Taulukko, k: float = 1.0) -> Taulukko:
    """K_ij = k * integraali grad(phi_i) . grad(phi_j) kolmion yli."""
    g, ala = elementti(p)
    tulos: Taulukko = k * ala * (g @ g.T)
    return tulos
# @loppu elementti


# @alku kokoaminen
def jaykkyys(verkko: Verkko, k: float = 1.0) -> sp.csr_array:
    """Globaali jäykkyysmatriisi: elementtimatriisit summataan
    paikoilleen solmunumeroiden mukaan."""
    rivit, sarakkeet, arvot = [], [], []
    for solmut in verkko.kolmiot:
        ke = elementtimatriisi(verkko.pisteet[solmut], k)
        for a in range(3):
            for b in range(3):
                rivit.append(solmut[a])
                sarakkeet.append(solmut[b])
                arvot.append(ke[a, b])
    n = len(verkko.pisteet)
    # COO-muoto summaa samaan paikkaan osuvat arvot muunnoksessa.
    return sp.coo_array((arvot, (rivit, sarakkeet)), shape=(n, n)).tocsr()


def kuorma(verkko: Verkko, f: Funktio) -> Taulukko:
    """Kuormavektori: integraali f * phi_i, kvadratuuripisteinä sivujen
    keskipisteet (tarkka toisen asteen polynomeille)."""
    b = np.zeros(len(verkko.pisteet))
    for solmut in verkko.kolmiot:
        p = verkko.pisteet[solmut]
        _, ala = elementti(p)
        keski = 0.5 * (p + np.roll(p, -1, axis=0))     # sivut 01, 12, 20
        arvot = f(keski[:, 0], keski[:, 1])
        for a in range(3):          # phi_a = 1/2 kahdella sivullaan
            b[solmut[a]] += ala / 3.0 * 0.5 * (arvot[a] + arvot[a - 1])
    return b
# @loppu kokoaminen


def massa(verkko: Verkko) -> sp.csr_array:
    """Massamatriisi: integraali phi_i * phi_j."""
    rivit, sarakkeet, arvot = [], [], []
    malli = (np.ones((3, 3)) + np.eye(3)) / 12.0
    for solmut in verkko.kolmiot:
        _, ala = elementti(verkko.pisteet[solmut])
        for a in range(3):
            for b in range(3):
                rivit.append(solmut[a])
                sarakkeet.append(solmut[b])
                arvot.append(ala * malli[a, b])
    n = len(verkko.pisteet)
    return sp.coo_array((arvot, (rivit, sarakkeet)), shape=(n, n)).tocsr()


# @alku reuna
def reunamatriisi(verkko: Verkko, sarmat: Indeksit,
                  h: float) -> sp.csr_array:
    """Konvektioreuna: integraali h * phi_i * phi_j reunasärmillä."""
    n = len(verkko.pisteet)
    tulos = sp.lil_array((n, n))
    for a, b in sarmat:
        pituus = float(np.linalg.norm(verkko.pisteet[b] - verkko.pisteet[a]))
        tulos[a, a] += h * pituus / 3.0
        tulos[b, b] += h * pituus / 3.0
        tulos[a, b] += h * pituus / 6.0
        tulos[b, a] += h * pituus / 6.0
    return tulos.tocsr()


def reunakuorma(verkko: Verkko, sarmat: Indeksit, q: float) -> Taulukko:
    """Annettu vuo q (sisään positiivinen): puolet särmän kummallekin
    solmulle."""
    b = np.zeros(len(verkko.pisteet))
    for s, t in sarmat:
        pituus = float(np.linalg.norm(verkko.pisteet[t] - verkko.pisteet[s]))
        b[s] += 0.5 * q * pituus
        b[t] += 0.5 * q * pituus
    return b
# @loppu reuna


# @alku dirichlet
def ratkaise(a: sp.csr_array, b: Taulukko, kiinni: Indeksit,
             arvot: Taulukko) -> Taulukko:
    """Ratkaisee A u = b, kun u tunnetaan solmuissa `kiinni`."""
    n = len(b)
    vapaat = np.setdiff1d(np.arange(n), kiinni)
    u = np.zeros(n)
    u[kiinni] = arvot
    # Tunnetut arvot siirretään oikealle puolelle.
    oikea = b[vapaat] - a[vapaat][:, kiinni] @ arvot
    u[vapaat] = spsolve(a[vapaat][:, vapaat].tocsc(), oikea)
    return u
# @loppu dirichlet


def l2_virhe(verkko: Verkko, u: Taulukko, tarkka: Funktio) -> float:
    """L2-virhe sivujen keskipisteiden kvadratuurilla."""
    p = verkko.pisteet[verkko.kolmiot]                 # (m, 3, 2)
    keski = 0.5 * (p + np.roll(p, -1, axis=1))
    uh = 0.5 * (u[verkko.kolmiot] + np.roll(u[verkko.kolmiot], -1, axis=1))
    ero = uh - tarkka(keski[:, :, 0], keski[:, :, 1])
    v1, v2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
    alat = 0.5 * (v1[:, 0] * v2[:, 1] - v1[:, 1] * v2[:, 0])
    return float(np.sqrt(np.sum(alat[:, None] / 3.0 * ero**2)))
