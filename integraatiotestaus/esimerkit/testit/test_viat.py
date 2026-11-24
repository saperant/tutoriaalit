"""Verkkovikojen simulointi vikaproxyllä (Toxiproxyn periaate)."""

from __future__ import annotations

import urllib.request
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import OperationalError
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from testiapu import kontit
from testiapu.kontit import osoite
from varasto.hinnat import HintaAsiakas, HintaVirhe


def ohjaa(proxy: DockerContainer, komento: str) -> None:
    pyynto = urllib.request.Request(f"{osoite(proxy, 8474)}{komento}",
                                    method="POST")
    with urllib.request.urlopen(pyynto, timeout=5):
        pass


# @alku verkko
@pytest.fixture(scope="module")
def verkko(apukuva: str) -> Iterator[Network]:
    """Oma Docker-verkko: kontit tavoittavat toisensa nimillä."""
    with Network() as n:
        yield n


@pytest.fixture(scope="module")
def hinnat_proxyn_takana(
        verkko: Network) -> Iterator[DockerContainer]:
    palvelu = (kontit.hintapalvelu().with_network(verkko)
               .with_network_aliases("hinnat"))
    with palvelu, kontit.vikaproxy(verkko, "hinnat:8080") as proxy:
        yield proxy
# @loppu verkko


# @alku viivetesti
def test_viive_ylittaa_aikarajan(
        hinnat_proxyn_takana: DockerContainer) -> None:
    proxy = hinnat_proxyn_takana
    asiakas = HintaAsiakas(osoite(proxy, 8666), aikaraja=0.3,
                           yritykset=2)
    assert asiakas.hae("ABC-1").hinta_snt == 1990

    ohjaa(proxy, "/viive?ms=1000")
    try:
        with pytest.raises(HintaVirhe, match="2 yrityksellä"):
            asiakas.hae("ABC-1")
    finally:
        ohjaa(proxy, "/palauta")
    assert asiakas.hae("ABC-1").hinta_snt == 1990
# @loppu viivetesti


@pytest.fixture(scope="module")
def kanta_proxyn_takana(
        verkko: Network) -> Iterator[tuple[Engine, DockerContainer]]:
    tietokanta = (kontit.postgres().with_network(verkko)
                  .with_network_aliases("tietokanta"))
    with tietokanta, kontit.vikaproxy(verkko, "tietokanta:5432") as p:
        url = (f"postgresql+psycopg://varasto:testi@"
               f"{p.get_container_host_ip()}:{p.get_exposed_port(8666)}"
               f"/varasto")
        kone = create_engine(url, pool_pre_ping=True,
                             connect_args={"connect_timeout": 2})
        yield kone, p
        kone.dispose()


# @alku katkotesti
def test_yhteysallas_toipuu_katkosta(
        kanta_proxyn_takana: tuple[Engine, DockerContainer]) -> None:
    kone, proxy = kanta_proxyn_takana
    with kone.connect() as y:
        assert y.execute(text("SELECT 1")).scalar() == 1

    ohjaa(proxy, "/katkaise")
    try:
        with pytest.raises(OperationalError), kone.connect() as y:
            y.execute(text("SELECT 1"))
    finally:
        ohjaa(proxy, "/palauta")

    # pool_pre_ping hylkää katkenneet yhteydet ja avaa uudet.
    with kone.connect() as y:
        assert y.execute(text("SELECT 1")).scalar() == 1
# @loppu katkotesti
