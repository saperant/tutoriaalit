"""Skalaarin kuljetus tunnetussa virtauksessa kontrollitilavuuksilla.

Tasainen suorakulmainen hila, ruudun sivu h. Pitoisuus c on ruutujen
keskipisteissä, nopeus ruutujen pinnoilla. Tasapainotilan tase jokaiselle
ruudulle: pintojen läpi lähtevä määrä = ruudussa syntyvä määrä."""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

Taulukko = npt.NDArray[np.float64]
Indeksit = npt.NDArray[np.intp]


# @alku hila
@dataclass(frozen=True)
class Hila:
    nx: int
    ny: int
    h: float

    def numero(self) -> Indeksit:
        """Ruudun (i, j) järjestysnumero yhtälöryhmässä."""
        return np.arange(self.nx * self.ny).reshape(self.nx, self.ny)

    def keskipisteet(self) -> tuple[Taulukko, Taulukko]:
        x: Taulukko = (np.arange(self.nx, dtype=np.float64) + 0.5) * self.h
        y: Taulukko = (np.arange(self.ny, dtype=np.float64) + 0.5) * self.h
        return x, y


def tasainen_tuuli(hila: Hila, ux: float, uy: float
                   ) -> tuple[Taulukko, Taulukko]:
    """Nopeus pystypinnoilla (nx + 1, ny) ja vaakapinnoilla (nx, ny + 1)."""
    return (np.full((hila.nx + 1, hila.ny), ux),
            np.full((hila.nx, hila.ny + 1), uy))
# @loppu hila


# @alku pinta
def pinnan_kertoimet(virta: Taulukko, d: float, kaavio: str
                     ) -> tuple[Taulukko, Taulukko]:
    """Pinnan vuo ruudusta A ruutuun B muodossa ka c_A + kb c_B.

    virta on pinnan läpi kulkeva tilavuusvirta A:sta B:hen (nopeus kertaa
    pinnan pituus). Diffuusiovuo on -d (c_B - c_A), koska pinnan pituus
    ja ruutujen etäisyys ovat molemmat h."""
    if kaavio == "vastavirta":
        ka = np.maximum(virta, 0.0) + d      # arvo otetaan tulosuunnasta
        kb = np.minimum(virta, 0.0) - d
    elif kaavio == "keskeis":
        ka = 0.5 * virta + d                 # pintojen arvojen keskiarvo
        kb = 0.5 * virta - d
    else:
        raise ValueError(f"tuntematon kaavio: {kaavio}")
    return ka, kb
# @loppu pinta


# @alku kokoa
def kokoa(hila: Hila, u: Taulukko, v: Taulukko, d: float, kaavio: str,
          lahde: Taulukko, c_sisaan: float = 0.0
          ) -> tuple[sp.csr_array, Taulukko]:
    """Tasapainotilan yhtälöryhmä A c = b.

    Reunoilla, joilta virtaus tulee sisään, pitoisuus on c_sisaan.
    Reunoilla, joilta virtaus lähtee, aine poistuu virtauksen mukana."""
    nro = hila.numero()
    h = hila.h
    rivit: list[Indeksit] = []
    sarakkeet: list[Indeksit] = []
    arvot: list[Taulukko] = []
    b = lahde.astype(np.float64).ravel().copy()

    def lisaa(r: Indeksit, s: Indeksit, a: Taulukko) -> None:
        rivit.append(r.ravel())
        sarakkeet.append(s.ravel())
        arvot.append(a.ravel())

    # Sisäpinnat: sama vuo lähtee ruudusta A ja saapuu ruutuun B.
    for a_ruudut, b_ruudut, virta in (
            (nro[:-1, :], nro[1:, :], u[1:-1, :] * h),
            (nro[:, :-1], nro[:, 1:], v[:, 1:-1] * h)):
        ka, kb = pinnan_kertoimet(virta, d, kaavio)
        lisaa(a_ruudut, a_ruudut, ka)
        lisaa(a_ruudut, b_ruudut, kb)
        lisaa(b_ruudut, a_ruudut, -ka)
        lisaa(b_ruudut, b_ruudut, -kb)

    # Reunapinnat: ulos on virtaus ruudusta poispäin.
    for ruudut, ulos in (
            (nro[0, :], -u[0, :] * h), (nro[-1, :], u[-1, :] * h),
            (nro[:, 0], -v[:, 0] * h), (nro[:, -1], v[:, -1] * h)):
        sisaan = ulos < 0.0
        # Ulosvirtaus vie ruudun oman pitoisuuden mukanaan.
        lisaa(ruudut, ruudut, np.where(sisaan, 0.0, ulos))
        # Sisäänvirtaus tuo pitoisuuden c_sisaan; reunaan on matkaa h / 2.
        lisaa(ruudut, ruudut, np.where(sisaan, 2.0 * d, 0.0))
        np.add.at(b, ruudut,
                  np.where(sisaan, (2.0 * d - ulos) * c_sisaan, 0.0))

    n = hila.nx * hila.ny
    a = sp.coo_array((np.concatenate(arvot),
                      (np.concatenate(rivit), np.concatenate(sarakkeet))),
                     shape=(n, n)).tocsr()
    return a, b


def ratkaise(hila: Hila, u: Taulukko, v: Taulukko, d: float, kaavio: str,
             lahde: Taulukko, c_sisaan: float = 0.0) -> Taulukko:
    a, b = kokoa(hila, u, v, d, kaavio, lahde, c_sisaan)
    c: Taulukko = spsolve(a, b)
    return c.reshape(hila.nx, hila.ny)
# @loppu kokoa


# @alku tase
def ulosvirtaus(hila: Hila, u: Taulukko, v: Taulukko, c: Taulukko,
                d: float, c_sisaan: float = 0.0) -> float:
    """Reunojen läpi poistuva ainemäärä aikayksikössä: virtauksen mukana
    ulosvirtausreunoilla ja diffuusiolla sisäänvirtausreunoilla."""
    h = hila.h
    summa = 0.0
    for arvot, ulos in ((c[0, :], -u[0, :] * h), (c[-1, :], u[-1, :] * h),
                        (c[:, 0], -v[:, 0] * h), (c[:, -1], v[:, -1] * h)):
        sisaan = ulos < 0.0
        summa += float(np.sum(np.where(
            sisaan, (2.0 * d - ulos) * (arvot - c_sisaan) + ulos * arvot,
            ulos * arvot)))
    return summa
# @loppu tase
