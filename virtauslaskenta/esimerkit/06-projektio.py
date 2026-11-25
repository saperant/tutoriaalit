"""Projektio porrastetulla hilalla: mistä tahansa nopeuskentästä tehdään
lähteetön vähentämällä siitä sopivan potentiaalin gradientti.

Suljettu neliö, n x n ruutua. Vaakanopeus u on pystypinnoilla
(n + 1, n), pystynopeus v vaakapinnoilla (n, n + 1) ja potentiaali
ruutujen keskellä (n, n)."""

import math

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

Taulukko = npt.NDArray[np.float64]

N = 32
H = 1.0 / N


# @alku operaattorit
def divergenssi(u: Taulukko, v: Taulukko) -> Taulukko:
    """Ruudun pintojen läpi lähtevä virta tilavuutta kohden."""
    tulos: Taulukko = (u[1:, :] - u[:-1, :] + v[:, 1:] - v[:, :-1]) / H
    return tulos


def gradientti(phi: Taulukko) -> tuple[Taulukko, Taulukko]:
    """Gradientti sisäpinnoilla; seinillä se on nolla (ei läpivirtausta)."""
    gx = np.zeros((N + 1, N))
    gy = np.zeros((N, N + 1))
    gx[1:-1, :] = (phi[1:, :] - phi[:-1, :]) / H
    gy[:, 1:-1] = (phi[:, 1:] - phi[:, :-1]) / H
    return gx, gy


def laplace() -> sp.csr_array:
    """div(grad) matriisina: yhdessä suunnassa tridiag(1, -2, 1), jonka
    reunarivit ovat (-1, 1), koska seinän läpi ei ole vuota."""
    lavistaja = [-1.0] + [-2.0] * (N - 2) + [-1.0]
    sivu = [1.0] * (N - 1)
    t = sp.diags_array([sivu, lavistaja, sivu], offsets=[-1, 0, 1])
    yksikko = sp.eye_array(N)
    return ((sp.kron(t, yksikko) + sp.kron(yksikko, t)) / H**2).tocsr()
# @loppu operaattorit


# @alku projektio
def projisoi(u: Taulukko, v: Taulukko) -> tuple[Taulukko, Taulukko, Taulukko]:
    """Ratkaisee lap(phi) = div(u) ja palauttaa u - grad(phi) sekä phin."""
    a = laplace().tolil()
    a[0, 0] -= 1.0 / H**2        # phi on määrätty vakiota vaille: kiinnitys
    phi: Taulukko = spsolve(a.tocsr(), divergenssi(u, v).ravel())
    phi = phi.reshape(N, N)
    gx, gy = gradientti(phi)
    return u - gx, v - gy, phi
# @loppu projektio


# @alku koe
def energia(u: Taulukko, v: Taulukko) -> float:
    return 0.5 * float(np.sum(u**2) + np.sum(v**2)) * H**2


kulmat: Taulukko = np.linspace(0.0, 1.0, N + 1)
kesket: Taulukko = (np.arange(N, dtype=np.float64) + 0.5) * H
# Pyörre virtafunktiosta psi (kulmissa): lähteetön jo hilalla.
psi = (np.sin(math.pi * kulmat)[:, None] ** 2
       * np.sin(math.pi * kulmat)[None, :] ** 2)
u_pyorre = (psi[:, 1:] - psi[:, :-1]) / H
v_pyorre = -(psi[1:, :] - psi[:-1, :]) / H
# Lähde–nielu-kenttä jonkin potentiaalin gradienttina.
potentiaali = (0.2 * np.cos(math.pi * kesket)[:, None]
               * np.cos(2.0 * math.pi * kesket)[None, :])
gx, gy = gradientti(potentiaali)
u, v = u_pyorre + gx, v_pyorre + gy

u2, v2, phi = projisoi(u, v)
ennen = float(np.max(np.abs(divergenssi(u, v))))
jalkeen = float(np.max(np.abs(divergenssi(u2, v2))))
ero = max(float(np.max(np.abs(u2 - u_pyorre))),
          float(np.max(np.abs(v2 - v_pyorre))))
print(f"suurin divergenssi ennen projektiota: {ennen:.2f}")
print(f"suurin divergenssi projektion jälkeen alle 1e-10: {jalkeen < 1e-10}")
print(f"jäljelle jäi alkuperäinen pyörre (ero alle 1e-10): {ero < 1e-10}")
e_koko, e_pyorre, e_grad = energia(u, v), energia(u2, v2), energia(gx, gy)
print(f"liike-energia: koko {e_koko:.5f} = pyörre {e_pyorre:.5f}"
      f" + gradienttiosa {e_grad:.5f}")
# @loppu koe
