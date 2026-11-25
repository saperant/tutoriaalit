"""Porrastettu verkko: solmut sinne, missä virhe syntyy.

L-alueen kulmasingulariteetti (luku 7) pilaa tasaisen tihennyksen
kertaluvun. Verrataan tasaista tihennystä verkkoon, jonka kolmiot
pienenevät kulmaa kohti säännöllä h <= H sqrt(r)."""

import math
import sys
from pathlib import Path

import numpy as np
import skfem as fem
from skfem.models.poisson import laplace

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import Taulukko, l_alue  # noqa: E402


def kulma(x: Taulukko, y: Taulukko) -> Taulukko:
    theta = np.mod(np.arctan2(y, x), 2.0 * math.pi)
    tulos: Taulukko = np.hypot(x, y) ** (2 / 3) * np.sin(2 * theta / 3)
    return tulos


# @alku virhe
def l2_virhe(verkko: fem.MeshTri) -> tuple[int, float]:
    kanta = fem.Basis(verkko, fem.ElementTriP1())
    reuna = kanta.get_dofs().flatten()
    arvot = np.zeros(kanta.N)
    arvot[reuna] = kulma(kanta.doflocs[0, reuna], kanta.doflocs[1, reuna])
    u = fem.solve(*fem.condense(laplace.assemble(kanta), np.zeros(kanta.N),
                                x=arvot, D=reuna))
    nelio = fem.Functional(
        lambda w: (w["uh"] - kulma(w.x[0], w.x[1])) ** 2
    ).assemble(kanta, uh=kanta.interpolate(u))
    return kanta.N, math.sqrt(float(nelio))
# @loppu virhe


# @alku tihennys
def porrasta(verkko: fem.MeshTri, koko: float) -> fem.MeshTri:
    """Jakaa kolmioita, kunnes jokaisen pisin sivu on enintään
    koko * sqrt(etäisyys kulmasta). Kirjasto jakaa myös naapureita sen
    verran, että verkko pysyy yhtenäisenä (ei roikkuvia solmuja)."""
    for _ in range(40):
        p = verkko.p[:, verkko.t]                      # (2, 3, kolmioita)
        sivut = [np.hypot(*(p[:, i] - p[:, (i + 1) % 3])) for i in range(3)]
        keski = p.mean(axis=1)
        raja = koko * np.hypot(keski[0], keski[1]) ** 0.5
        liian_suuret = np.flatnonzero(np.max(sivut, axis=0) > raja)
        if len(liian_suuret) == 0:
            break
        verkko = verkko.refined(liian_suuret)
    return verkko
# @loppu tihennys


# @alku koe
def kertaluku(n0: int, e0: float, n1: int, e1: float) -> str:
    """Kertaluku solmumäärästä: tasossa h on verrannollinen 1/sqrt(N)."""
    return f"{-2.0 * math.log(e1 / e0) / math.log(n1 / n0):7.2f}"


oma = l_alue(4)
perus = fem.MeshTri(np.ascontiguousarray(oma.pisteet.T),
                    np.ascontiguousarray(oma.kolmiot.T))
print("tasainen tihennys              porrastettu verkko")
print(" solmuja   L2-virhe  kertal.     solmuja   L2-virhe  kertal.")
tasainen = perus
ed_t = ed_p = (0, 0.0)
for koko in (0.5, 0.25, 0.125, 0.0625):
    tasainen = tasainen.refined()
    n1, e1 = l2_virhe(tasainen)
    n2, e2 = l2_virhe(porrasta(perus, koko))
    p1 = kertaluku(*ed_t, n1, e1) if ed_t[0] else "      -"
    p2 = kertaluku(*ed_p, n2, e2) if ed_p[0] else "      -"
    print(f"{n1:8d} {e1:10.2e} {p1} {n2:11d} {e2:10.2e} {p2}")
    ed_t, ed_p = (n1, e1), (n2, e2)
# @loppu koe
