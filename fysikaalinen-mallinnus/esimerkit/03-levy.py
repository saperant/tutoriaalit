"""Stationaarinen lämpötila neliölevyssä: viiden pisteen kaava ja harva
yhtälöryhmä. Alareuna on 100 °C, muut reunat 0 °C."""

import math

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

Taulukko = npt.NDArray[np.float64]
T_KUUMA = 100.0


# @alku kokoaminen
def ratkaise(m: int) -> Taulukko:
    """m x m sisäpistettä yksikköneliössä; palauttaa taulukon u[j, i],
    jossa j on rivi (y) ja i sarake (x)."""
    h = 1.0 / (m + 1)
    t = sp.diags_array([-1.0, 2.0, -1.0], offsets=[-1, 0, 1],
                       shape=(m, m))
    yksikko = sp.eye_array(m)
    a = (sp.kron(yksikko, t) + sp.kron(t, yksikko)).tocsr() / h**2
    b = np.zeros((m, m))
    b[0, :] = T_KUUMA / h**2          # alin sisärivi näkee kuuman reunan
    u: Taulukko = spsolve(a, b.ravel())
    return u.reshape(m, m)
# @loppu kokoaminen


# @alku sarja
def tarkka(x: float, y: float, termeja: int = 200) -> float:
    """Muuttujien erottelulla saatu sarjaratkaisu."""
    summa = 0.0
    for n in range(1, 2 * termeja, 2):           # vain parittomat
        k = n * math.pi
        # sinh(k(1 - y))/sinh(k) kirjoitettuna ilman ylivuotoa
        suhde = (math.exp(-k * y) * (1.0 - math.exp(-2.0 * k * (1.0 - y)))
                 / (1.0 - math.exp(-2.0 * k)))
        summa += 4.0 / k * math.sin(k * x) * suhde
    return T_KUUMA * summa
# @loppu sarja


# @alku vertailu
print("   m  keskipiste   piste (0.5, 0.25)  virhe     kertaluku")
edellinen = 0.0
viite = tarkka(0.5, 0.25)
for m in (7, 15, 31, 63, 127):
    u = ratkaise(m)
    keski = u[m // 2, m // 2]
    arvo = u[(m + 1) // 4 - 1, m // 2]            # y = 0.25, x = 0.5
    virhe = abs(arvo - viite)
    p = f"{math.log2(edellinen / virhe):8.2f}" if edellinen else "       -"
    print(f"{m:4d} {keski:11.6f} {arvo:18.4f} {virhe:9.2e} {p}")
    edellinen = virhe
print(f"sarjaratkaisu pisteessä (0.5, 0.25): {viite:.4f}")
# @loppu vertailu
