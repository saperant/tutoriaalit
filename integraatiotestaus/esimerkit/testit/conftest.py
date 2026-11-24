"""Testien yhteiset fixturet: kontit, tietokanta ja eristys."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
import redis
from sqlalchemy import Connection, Engine, create_engine
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
from testcontainers.core.container import DockerContainer

from testiapu import kontit
from varasto.migraatiot import migroi
from varasto.varasto import MuistiVarasto, PgVarasto, Varasto


# @alku istunto
@pytest.fixture(scope="session")
def pg() -> Iterator[PostgresContainer]:
    """Yksi PostgreSQL koko testiajolle: käynnistys maksaa sekunteja."""
    with kontit.postgres() as kontti:
        yield kontti


@pytest.fixture(scope="session")
def kone(pg: PostgresContainer) -> Iterator[Engine]:
    """Yhteysallas, jonka skeema on migroitu kerran."""
    kone = create_engine(pg.get_connection_url(), pool_pre_ping=True)
    migroi(kone)
    yield kone
    kone.dispose()
# @loppu istunto


# @alku yhteys
@pytest.fixture
def yhteys(kone: Engine) -> Iterator[Connection]:
    """Jokainen testi omassa transaktiossaan, joka perutaan lopuksi.

    PgVarasto tekee omat transaktionsa tallennuspisteinä tämän sisällä,
    joten testin kirjoitukset eivät näy muille testeille."""
    with kone.connect() as y:
        transaktio = y.begin()
        try:
            yield y
        finally:
            transaktio.rollback()
# @loppu yhteys


# @alku sopimus
@pytest.fixture(params=["muisti", "postgres"])
def varasto(request: pytest.FixtureRequest) -> Varasto:
    """Sama testi ajetaan väärennökselle ja oikealle tietokannalle."""
    if request.param == "muisti":
        return MuistiVarasto()
    return PgVarasto(request.getfixturevalue("yhteys"))
# @loppu sopimus


# @alku muut
@pytest.fixture(scope="session")
def redis_kontti() -> Iterator[RedisContainer]:
    with kontit.redis_kontti() as kontti:
        yield kontti


@pytest.fixture
def r(redis_kontti: RedisContainer) -> Iterator[redis.Redis]:
    """Tyhjä Redis jokaiselle testille."""
    asiakas = redis.Redis(host=redis_kontti.get_container_host_ip(),
                          port=int(redis_kontti.get_exposed_port(6379)))
    asiakas.flushdb()
    yield asiakas
    asiakas.close()


@pytest.fixture(scope="session")
def apukuva() -> str:
    kontit.apukuva().build()
    return "rakennettu"


@pytest.fixture(scope="session")
def hintapalvelu(apukuva: str) -> Iterator[DockerContainer]:
    with kontit.hintapalvelu() as kontti:
        yield kontti
# @loppu muut
