"""Yhtälöryhmän koko ja ratkaisijan työ: täyttyminen ja iteraatiot.

Poissonin tehtävä neliössä omalla kirjastolla koottuna. Suora
ratkaisija maksaa hajotelman täyttymisenä, liittogradienttimenetelmä
iteraatioina, joiden määrä kasvaa verkon tihentyessä."""

import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
from scipy.sparse.linalg import cg, splu

Taulukko = npt.NDArray[np.float64]

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import jaykkyys, suorakulmio  # noqa: E402


# @alku mittaus
def iteraatiot(a: sp.csc_array, b: Taulukko) -> int:
    """Liittogradienttimenetelmän kierrokset suhteelliseen
    jäännökseen 1e-8 asti."""
    kierrokset = 0

    def laskuri(_: Taulukko) -> None:
        nonlocal kierrokset
        kierrokset += 1

    _, tila = cg(a, b, rtol=1e-8, callback=laskuri)
    if tila != 0:
        raise RuntimeError("liittogradientti ei supennut")
    return kierrokset


print("ruutuja  tuntemattomia  alkioita  täyttö luonn.  täyttö järj."
      "  CG-kierroksia")
for n in (16, 32, 64, 128):
    verkko = suorakulmio(n, n)
    sisa = np.setdiff1d(np.arange(len(verkko.pisteet)),
                        verkko.reunasolmut())
    a = jaykkyys(verkko)[sisa][:, sisa].tocsc()
    b = np.full(len(sisa), 1.0 / n**2)
    taytto = []
    for jarjestys in ("NATURAL", "COLAMD"):
        lu = splu(a, permc_spec=jarjestys)
        taytto.append((lu.L.nnz + lu.U.nnz) / a.nnz)
    # Kierrosmäärä voi vaihdella yhdellä koneen mukaan: pyöristetään.
    kierroksia = round(iteraatiot(a, b), -1)
    print(f"{n:7d} {len(sisa):14d} {a.nnz:9d} {taytto[0]:14.1f} "
          f"{taytto[1]:13.1f} {'noin ' + str(kierroksia):>14}")
# @loppu mittaus
