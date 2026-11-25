"""Sama ulokepalkki scikit-fem-kirjastolla: lineaarinen ja toisen
asteen kolmio rinnakkain."""

import sys
from pathlib import Path

import numpy as np
import skfem as fem
from skfem.models.elasticity import lame_parameters, linear_elasticity

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import suorakulmio  # noqa: E402

E_MODUULI, NU = 210e9, 0.3
PITUUS, KORKEUS, PAKSUUS = 1.0, 0.1, 0.01
VOIMA = 1000.0


# @alku malli
def taipuma(nx: int, ny: int, elementti: fem.Element) -> tuple[int, float]:
    oma = suorakulmio(nx, ny, PITUUS, KORKEUS)
    verkko = fem.MeshTri(np.ascontiguousarray(oma.pisteet.T),
                         np.ascontiguousarray(oma.kolmiot.T))
    kanta = fem.Basis(verkko, fem.ElementVector(elementti))
    # Kirjaston Lamén vakiot ovat tasovenymätilalle; tasojännitystila
    # saadaan korvaamalla lambda arvolla 2 lambda mu / (lambda + 2 mu).
    lam, mu = lame_parameters(E_MODUULI, NU)
    lam = 2.0 * lam * mu / (lam + 2.0 * mu)
    k = PAKSUUS * linear_elasticity(lam, mu).assemble(kanta)
    paa = fem.FacetBasis(verkko, kanta.elem, facets=verkko.facets_satisfying(
        lambda x: np.isclose(x[0], PITUUS)))
    f = fem.LinearForm(lambda v, w: -VOIMA / KORKEUS * v[1]).assemble(paa)
    kiinni = kanta.get_dofs(lambda x: np.isclose(x[0], 0.0))
    u = fem.solve(*fem.condense(k, f, D=kiinni))
    pystysuunta = kanta.get_dofs(
        lambda x: np.isclose(x[0], PITUUS)).all("u^2")
    return kanta.N, float(-u[pystysuunta].mean())
# @loppu malli


# @alku vertailu
hitaus = PAKSUUS * KORKEUS**3 / 12.0
teoria = (VOIMA * PITUUS**3 / (3.0 * E_MODUULI * hitaus)
          + VOIMA * PITUUS * 2.0 * (1.0 + NU)
          / (5.0 / 6.0 * E_MODUULI * PAKSUUS * KORKEUS))
print("   verkko   P1: vapausast.  osuus %   P2: vapausast.  osuus %")
for nx, ny in ((10, 1), (20, 2), (40, 4), (80, 8)):
    rivi = f"{nx:4d} x {ny:<2d}"
    for el in (fem.ElementTriP1(), fem.ElementTriP2()):
        n, d = taipuma(nx, ny, el)
        rivi += f" {n:15d} {100.0 * d / teoria:8.1f}"
    print(rivi)
# @loppu vertailu
