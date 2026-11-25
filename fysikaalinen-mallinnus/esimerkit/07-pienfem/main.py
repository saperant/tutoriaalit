"""pienfem-kirjaston tarkistukset: elementtimatriisi, paikkatesti,
vertailu viiden pisteen kaavaan ja suppenemisen kertaluku."""

import math

import numpy as np
import scipy.sparse as sp

from pienfem import (
    Taulukko,
    elementtimatriisi,
    jaykkyys,
    kuorma,
    l2_virhe,
    ratkaise,
    suorakulmio,
)

# @alku elementti
viite = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
ke = elementtimatriisi(viite)
print("suorakulmaisen yksikkökolmion elementtimatriisi:")
for rivi in ke:
    print("  " + " ".join(f"{a:5.2f}" for a in rivi))
print(f"rivisummat nollia: {bool(np.allclose(ke.sum(axis=1), 0.0))}")
# @loppu elementti

# @alku paikkatesti
verkko = suorakulmio(5, 3, 2.0, 1.0)
x, y = verkko.pisteet[:, 0], verkko.pisteet[:, 1]
lineaarinen = 1.0 + 2.0 * x - 3.0 * y
reuna = verkko.reunasolmut()
u = ratkaise(jaykkyys(verkko), np.zeros(len(x)), reuna, lineaarinen[reuna])
print(f"paikkatesti: suurin virhe alle 1e-12: "
      f"{bool(np.max(np.abs(u - lineaarinen)) < 1e-12)}")
# @loppu paikkatesti

# @alku viisipiste
m = 6
verkko = suorakulmio(m + 1, m + 1)
sisa = np.setdiff1d(np.arange(len(verkko.pisteet)), verkko.reunasolmut())
k_sisa = jaykkyys(verkko)[sisa][:, sisa].toarray()
t = sp.diags_array([-1.0, 2.0, -1.0], offsets=[-1, 0, 1], shape=(m, m))
viisi = (sp.kron(sp.eye_array(m), t) + sp.kron(t, sp.eye_array(m))).toarray()
print(f"sama kuin viiden pisteen kaava: {bool(np.allclose(k_sisa, viisi))}")
# @loppu viisipiste


# @alku kertaluku
def tarkka(x: Taulukko, y: Taulukko) -> Taulukko:
    return np.sin(math.pi * x) * np.sin(math.pi * y)


def lahde(x: Taulukko, y: Taulukko) -> Taulukko:
    return 2.0 * math.pi**2 * tarkka(x, y)


print("ruutuja/sivu  solmuja   L2-virhe  kertaluku")
edellinen = 0.0
for n in (4, 8, 16, 32, 64):
    verkko = suorakulmio(n, n)
    reuna = verkko.reunasolmut()
    u = ratkaise(jaykkyys(verkko), kuorma(verkko, lahde), reuna,
                 np.zeros(len(reuna)))
    virhe = l2_virhe(verkko, u, tarkka)
    p = f"{math.log2(edellinen / virhe):9.2f}" if edellinen else "        -"
    print(f"{n:12d} {len(verkko.pisteet):8d} {virhe:10.2e} {p}")
    edellinen = virhe
# @loppu kertaluku
