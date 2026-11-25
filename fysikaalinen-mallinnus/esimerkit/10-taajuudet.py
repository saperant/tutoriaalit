"""Kielen ominaistaajuudet elementtimenetelmällä: yleistetty
ominaisarvotehtävä K v = omega² M v ja massamatriisin kaksi muotoa.

Kieli: pituus 1, aallon nopeus 1, päät kiinni. Tarkat kulmataajuudet
ovat omega_k = k pi."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import eigh

Taulukko = npt.NDArray[np.float64]


# @alku matriisit
def matriisit(n: int) -> tuple[Taulukko, Taulukko, Taulukko]:
    """Sisäsolmujen jäykkyysmatriisi sekä konsistentti ja keskitetty
    massamatriisi n tasavälisellä elementillä."""
    h = 1.0 / n
    yksi = np.eye(n - 1)
    sivu = np.eye(n - 1, k=1) + np.eye(n - 1, k=-1)
    k = (2.0 * yksi - sivu) / h
    konsistentti = h / 6.0 * (4.0 * yksi + sivu)    # integraali phi_i phi_j
    keskitetty = h * yksi                           # rivisummat lävistäjälle
    return k, konsistentti, keskitetty
# @loppu matriisit


# @alku moodit
n = 10
k, mk, ml = matriisit(n)
print(f"{n} elementtiä: kulmataajuudet ja virhe prosentteina")
print("moodi   tarkka  konsistentti   virhe   keskitetty   virhe")
wk = np.sqrt(eigh(k, mk, eigvals_only=True))
wl = np.sqrt(eigh(k, ml, eigvals_only=True))
for moodi in (1, 2, 3, 5, 9):
    tarkka = moodi * math.pi
    a, b = wk[moodi - 1], wl[moodi - 1]
    print(f"{moodi:5d} {tarkka:8.3f} {a:13.3f} {100 * (a / tarkka - 1):7.2f} "
          f"{b:12.3f} {100 * (b / tarkka - 1):7.2f}")
# @loppu moodit

# @alku kertaluku
print("\nalimman taajuuden virhe ja suurin taajuus")
print("elementtejä  konsist. virhe  kertal.  omega_max kons.  keskit.")
edellinen = 0.0
for n in (5, 10, 20, 40):
    k, mk, ml = matriisit(n)
    wk = np.sqrt(eigh(k, mk, eigvals_only=True))
    wl = np.sqrt(eigh(k, ml, eigvals_only=True))
    virhe = wk[0] / math.pi - 1.0
    p = f"{math.log2(edellinen / virhe):7.2f}" if edellinen else "      -"
    print(f"{n:11d} {virhe:15.2e} {p} {wk[-1]:16.1f} {wl[-1]:8.1f}")
    edellinen = virhe
print("eksplisiittisen aikaintegroinnin raja: dt < 2 / omega_max")
# @loppu kertaluku
