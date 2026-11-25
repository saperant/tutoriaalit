"""Kalvon ominaisarvot scikit-fem-kirjastolla: neliö ja L-alue.

Neliössä (sivu 1) tarkat ominaisarvot ovat pi² (m² + n²). L-alueen
(kolme yksikköneliötä) alimmat arvot tunnetaan kirjallisuudesta."""

import math
import sys
from pathlib import Path

import numpy as np
import skfem as fem
from scipy.sparse.linalg import eigsh
from skfem.models.poisson import laplace, mass

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import Verkko, l_alue, suorakulmio  # noqa: E402

# Fox, Henrici ja Moler (1967); tarkennetut arvot Betcke ja Trefethen
# (2005).
L_KIRJALLISUUS = [9.63972, 15.19725, 19.73921, 29.52148, 31.91264]


# @alku ominaisarvot
def ominaisarvot(verkko: Verkko, maara: int) -> list[float]:
    """Alimmat ominaisarvot toisen asteen kolmioilla."""
    kanta = fem.Basis(
        fem.MeshTri(np.ascontiguousarray(verkko.pisteet.T),
                    np.ascontiguousarray(verkko.kolmiot.T)),
        fem.ElementTriP2())
    vapaat = kanta.complement_dofs(kanta.get_dofs())
    k = laplace.assemble(kanta)[vapaat][:, vapaat]
    m = mass.assemble(kanta)[vapaat][:, vapaat]
    # Siirto ja käänteisiteraatio: alimmat arvot ovat lähinnä nollaa.
    arvot = eigsh(k, k=maara, M=m, sigma=0.0, which="LM",
                  return_eigenvectors=False)
    return sorted(float(a) for a in arvot)
# @loppu ominaisarvot


# @alku nelio
print("neliö, 16 x 16 ruutua:")
tarkat = sorted(math.pi**2 * (m * m + n * n)
                for m in range(1, 4) for n in range(1, 4))[:4]
for laskettu, tarkka in zip(ominaisarvot(suorakulmio(16, 16), 4), tarkat,
                            strict=True):
    print(f"  {laskettu:9.4f}  tarkka {tarkka:9.4f}  "
          f"ero {100 * (laskettu / tarkka - 1):.4f} %")
# @loppu nelio

# @alku l-alue
print("L-alue: ero kirjallisuusarvoon prosentteina")
print("  arvo     kirjallisuus   8 ruutua/sivu   16 ruutua/sivu")
karkea, tihea = ominaisarvot(l_alue(4), 5), ominaisarvot(l_alue(8), 5)
for i, viite in enumerate(L_KIRJALLISUUS):
    print(f"  {i + 1:4d} {viite:16.5f} {100 * (karkea[i] / viite - 1):15.4f} "
          f"{100 * (tihea[i] / viite - 1):16.4f}")
# @loppu l-alue
