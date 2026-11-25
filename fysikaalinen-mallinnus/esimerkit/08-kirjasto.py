"""Sama Poissonin tehtävä scikit-fem-kirjastolla.

1. Kirjaston kokoama matriisi on sama kuin luvun 7 oman kirjaston.
2. Elementin vaihto toisen asteen kolmioon on yhden rivin muutos.
3. L-alueella korkeampi aste ei auta: ratkaisun sileys rajoittaa."""

import math
import sys
from pathlib import Path

import numpy as np
import skfem as fem
from skfem.models.poisson import laplace

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import (  # noqa: E402
    Taulukko,
    Verkko,
    jaykkyys,
    l_alue,
    suorakulmio,
)


# @alku verkko
def kirjaston_verkko(verkko: Verkko) -> fem.MeshTri:
    """scikit-fem tallettaa pisteet ja kolmiot sarakkeittain."""
    return fem.MeshTri(np.ascontiguousarray(verkko.pisteet.T),
                       np.ascontiguousarray(verkko.kolmiot.T))
# @loppu verkko


# @alku sama
oma = suorakulmio(8, 8)
kanta = fem.Basis(kirjaston_verkko(oma), fem.ElementTriP1())
ero = abs(laplace.assemble(kanta) - jaykkyys(oma)).max()
print(f"matriisit samat (ero alle 1e-12): {bool(ero < 1e-12)}")
# @loppu sama


# @alku ratkaisu
def tarkka(x: Taulukko, y: Taulukko) -> Taulukko:
    return np.sin(math.pi * x) * np.sin(math.pi * y)


def l2_virhe(verkko: Verkko, elementti: fem.Element) -> tuple[int, float]:
    """Ratkaisee -lap u = 2 pi² sin(pi x) sin(pi y); palauttaa
    tuntemattomien määrän ja L2-virheen."""
    kanta = fem.Basis(kirjaston_verkko(verkko), elementti)
    a = laplace.assemble(kanta)
    b = fem.LinearForm(
        lambda v, w: 2.0 * math.pi**2 * tarkka(w.x[0], w.x[1]) * v
    ).assemble(kanta)
    u = fem.solve(*fem.condense(a, b, D=kanta.get_dofs()))
    nelio = fem.Functional(
        lambda w: (w["uh"] - tarkka(w.x[0], w.x[1])) ** 2
    ).assemble(kanta, uh=kanta.interpolate(u))
    return kanta.N, math.sqrt(float(nelio))
# @loppu ratkaisu


# @alku kertaluku
print("ruutuja   P1: tuntem.  virhe   kertal.   P2: tuntem.  virhe   kertal.")
ed = [0.0, 0.0]
for n in (4, 8, 16, 32):
    rivi = f"{n:7d}"
    for i, el in enumerate((fem.ElementTriP1(), fem.ElementTriP2())):
        maara, virhe = l2_virhe(suorakulmio(n, n), el)
        p = f"{math.log2(ed[i] / virhe):6.2f}" if ed[i] else "     -"
        rivi += f" {maara:12d} {virhe:9.1e} {p}"
        ed[i] = virhe
    print(rivi)
# @loppu kertaluku


# @alku l-alue
def kulma(x: Taulukko, y: Taulukko) -> Taulukko:
    theta = np.mod(np.arctan2(y, x), 2.0 * math.pi)
    tulos: Taulukko = np.hypot(x, y) ** (2 / 3) * np.sin(2 * theta / 3)
    return tulos


print("\nL-alue, ratkaisu r^(2/3) sin(2 theta/3):")
print("ruutuja   P1-virhe  kertal.   P2-virhe  kertal.")
ed = [0.0, 0.0]
for n in (4, 8, 16, 32):
    rivi = f"{n:7d}"
    for i, el in enumerate((fem.ElementTriP1(), fem.ElementTriP2())):
        kanta = fem.Basis(kirjaston_verkko(l_alue(n)), el)
        reuna = kanta.get_dofs()
        paikat = kanta.doflocs[:, reuna.flatten()]
        arvot = np.zeros(kanta.N)
        arvot[reuna.flatten()] = kulma(paikat[0], paikat[1])
        u = fem.solve(*fem.condense(laplace.assemble(kanta),
                                    np.zeros(kanta.N), x=arvot, D=reuna))
        nelio = fem.Functional(
            lambda w: (w["uh"] - kulma(w.x[0], w.x[1])) ** 2
        ).assemble(kanta, uh=kanta.interpolate(u))
        virhe = math.sqrt(float(nelio))
        p = f"{math.log2(ed[i] / virhe):7.2f}" if ed[i] else "      -"
        rivi += f" {virhe:10.1e} {p}"
        ed[i] = virhe
    print(rivi)
# @loppu l-alue
