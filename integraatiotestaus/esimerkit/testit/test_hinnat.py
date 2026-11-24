"""Hinta-asiakas oikeaa HTTP-palvelua (väärennöskonttia) vasten."""

from __future__ import annotations

import urllib.request

import pytest
from testcontainers.core.container import DockerContainer

from testiapu.kontit import osoite
from varasto.hinnat import HintaAsiakas, HintaVirhe


def aseta_virheet(palvelu: DockerContainer, n: int) -> None:
    pyynto = urllib.request.Request(
        f"{osoite(palvelu, 8080)}/hallinta/virheet?n={n}", method="POST")
    with urllib.request.urlopen(pyynto, timeout=5):
        pass


# @alku hintatestit
def test_hinta_haetaan(hintapalvelu: DockerContainer) -> None:
    asiakas = HintaAsiakas(osoite(hintapalvelu, 8080))
    hinta = asiakas.hae("abc-1")
    assert (hinta.sku, hinta.hinta_snt, hinta.valuutta) == (
        "ABC-1", 1990, "EUR")


def test_tuntematon_sku_ei_yrita_uudelleen(
        hintapalvelu: DockerContainer) -> None:
    asiakas = HintaAsiakas(osoite(hintapalvelu, 8080))
    with pytest.raises(HintaVirhe, match="HTTP 404"):
        asiakas.hae("EI-OLE")


def test_tilapainen_503_yritetaan_uudelleen(
        hintapalvelu: DockerContainer) -> None:
    aseta_virheet(hintapalvelu, 2)
    asiakas = HintaAsiakas(osoite(hintapalvelu, 8080), yritykset=3)
    assert asiakas.hae("XYZ-9").hinta_snt == 450


def test_pysyva_503_paattyy_virheeseen(
        hintapalvelu: DockerContainer) -> None:
    aseta_virheet(hintapalvelu, 3)
    asiakas = HintaAsiakas(osoite(hintapalvelu, 8080), yritykset=3)
    with pytest.raises(HintaVirhe, match="3 yrityksellä"):
        asiakas.hae("XYZ-9")
# @loppu hintatestit
