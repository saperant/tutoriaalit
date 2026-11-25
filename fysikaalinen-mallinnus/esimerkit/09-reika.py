"""Reikälevy vedossa: jännityskeskittymä ja mallin oletuksen raja.

Neliölevyn (puolileveys W) keskellä on pyöreä reikä (säde a). Symmetrian
vuoksi mallinnetaan neljännes. Äärettömälle levylle tarkka ratkaisu
(Kirsch) antaa reiän reunalle kolminkertaisen jännityksen."""

import math

import numpy as np
import numpy.typing as npt
import skfem as fem
from skfem.helpers import sym_grad
from skfem.models.elasticity import lame_parameters, linear_elasticity

Taulukko = npt.NDArray[np.float64]
E_MODUULI, NU = 210e9, 0.3
W = 0.1                       # m
VETO = 1.0e6                  # Pa oikealla reunalla


# @alku verkko
def neljannes(a: float, nr: int, nt: int) -> fem.MeshTri:
    """Kuvattu rakenteinen verkko: säteet reiän reunalta ulkoreunalle.
    Solmut tihenevät reikää kohti (s² säteen suunnassa)."""
    s, kulma = np.meshgrid(np.linspace(0.0, 1.0, nr + 1) ** 2,
                           np.linspace(0.0, math.pi / 2, nt + 1))
    sisa_x, sisa_y = a * np.cos(kulma), a * np.sin(kulma)
    alempi = kulma <= math.pi / 4          # säde osuu oikeaan reunaan
    ulko_x = np.where(alempi, W, W / np.tan(np.maximum(kulma, 1e-12)))
    ulko_y = np.where(alempi, W * np.tan(kulma), W)
    x = sisa_x + s * (ulko_x - sisa_x)
    y = sisa_y + s * (ulko_y - sisa_y)
    kolmiot = []
    for j in range(nt):
        for i in range(nr):
            p = j * (nr + 1) + i
            q, r, t = p + 1, p + nr + 2, p + nr + 1
            kolmiot += [[p, q, r], [p, r, t]]
    return fem.MeshTri(np.ascontiguousarray(np.vstack([x.ravel(),
                                                       y.ravel()])),
                       np.ascontiguousarray(np.array(kolmiot).T))
# @loppu verkko


# @alku ratkaisu
def keskittyma(a: float, n: int) -> float:
    """Jännityksen s_xx suhde vetojännitykseen reiän laella (0, a)."""
    verkko = neljannes(a, n, n)
    kanta = fem.Basis(verkko, fem.ElementVector(fem.ElementTriP2()))
    lam, mu = lame_parameters(E_MODUULI, NU)
    lam = 2.0 * lam * mu / (lam + 2.0 * mu)            # tasojännitys
    k = linear_elasticity(lam, mu).assemble(kanta)
    oikea = fem.FacetBasis(verkko, kanta.elem,
                           facets=verkko.facets_satisfying(
                               lambda x: np.isclose(x[0], W)))
    f = fem.LinearForm(lambda v, w: VETO * v[0]).assemble(oikea)
    # Symmetriatasot: kohtisuora siirtymä on nolla.
    lukitut = np.concatenate([
        kanta.get_dofs(lambda x: np.isclose(x[0], 0.0)).all("u^1"),
        kanta.get_dofs(lambda x: np.isclose(x[1], 0.0)).all("u^2")])
    u = fem.solve(*fem.condense(k, f, D=lukitut))
    venyma = sym_grad(kanta.interpolate(u))
    sxx = 2.0 * mu * venyma[0, 0] + lam * (venyma[0, 0] + venyma[1, 1])
    # Jännitys projisoidaan jatkuvaksi solmuarvoiseksi kentäksi.
    solmuissa = kanta.with_element(fem.ElementTriP1()).project(sxx)
    laki = int(np.argmin(np.hypot(verkko.p[0], verkko.p[1] - a)))
    return float(solmuissa[laki]) / VETO
# @loppu ratkaisu


# @alku koe
print("  a/W   verkko 12   verkko 24   verkko 48")
for suhde in (0.05, 0.1, 0.2, 0.4):
    arvot = [keskittyma(suhde * W, n) for n in (12, 24, 48)]
    print(f"{suhde:5.2f} " + " ".join(f"{k:11.3f}" for k in arvot))
print("Kirschin ratkaisu äärettömälle levylle: 3.000")
# @loppu koe
