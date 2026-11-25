"""Diskretointivirheen arvio ilman tarkkaa ratkaisua: Richardsonin
ekstrapolointi ja verkkosuppenemisindeksi (GCI).

L-alue, -lap u = 1, u = 0 reunalla (esimerkiksi tasaisesti kuormitettu
kalvo). Tarkkaa ratkaisua ei tunneta. Tarkastellaan kahta suuretta:
ratkaisun integraalia ja suurinta gradienttia."""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import (  # noqa: E402
    elementti,
    jaykkyys,
    kuorma,
    l_alue,
    ratkaise,
)


# @alku suureet
def suureet(n: int) -> tuple[float, float]:
    """Palauttaa ratkaisun integraalin ja suurimman gradientin."""
    verkko = l_alue(n)
    reuna = verkko.reunasolmut()
    b = kuorma(verkko, lambda x, y: np.ones_like(x))
    u = ratkaise(jaykkyys(verkko), b, reuna, np.zeros(len(reuna)))
    suurin = 0.0
    for solmut in verkko.kolmiot:
        g, _ = elementti(verkko.pisteet[solmut])
        suurin = max(suurin, float(np.linalg.norm(u[solmut] @ g)))
    return float(b @ u), suurin          # integraali u dA = b . u
# @loppu suureet


# @alku gci
def arvio(karkea: float, keski: float, tihea: float) -> None:
    """Kolme verkkoa, tihennyssuhde 2: havaittu kertaluku,
    ekstrapoloitu arvo ja GCI tiheimmälle verkolle."""
    muutos1, muutos2 = keski - karkea, tihea - keski
    if muutos1 * muutos2 <= 0.0 or abs(muutos2) >= abs(muutos1):
        print("  muutokset eivät pienene: suure ei suppene, arviota ei ole")
        return
    p = math.log2(muutos1 / muutos2)
    ekstrapoloitu = tihea + muutos2 / (2.0**p - 1.0)
    gci = 1.25 * abs(muutos2 / tihea) / (2.0**p - 1.0)
    print(f"  havaittu kertaluku {p:.2f}, ekstrapoloitu {ekstrapoloitu:.5f}, "
          f"GCI {100.0 * gci:.2f} %")
# @loppu gci


# @alku koe
tulokset = {n: suureet(n) for n in (8, 16, 32, 64)}
print("ruutuja/sivu   integraali   suurin gradientti")
for n, (integraali, gradientti) in tulokset.items():
    print(f"{2 * n:12d} {integraali:12.5f} {gradientti:19.4f}")
print("integraali verkoista 16, 32 ja 64:")
arvio(*(tulokset[n][0] for n in (8, 16, 32)))
print("sama verkoista 32, 64 ja 128:")
arvio(*(tulokset[n][0] for n in (16, 32, 64)))
print("suurin gradientti verkoista 32, 64 ja 128:")
arvio(*(tulokset[n][1] for n in (16, 32, 64)))
# @loppu koe
