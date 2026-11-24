"""Konttien luonti testeille ja esimerkeille."""

from __future__ import annotations

from pathlib import Path

from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import (
    HttpWaitStrategy,
    LogMessageWaitStrategy,
)

from testiapu import kuvat

APUKUVAN_LAHDE = Path(__file__).resolve().parent.parent / "apukuva"


# @alku postgres
def postgres() -> PostgresContainer:
    """PostgreSQL, johon yhdistetään psycopg-ajurilla (psycopg 3)."""
    return PostgresContainer(kuvat.POSTGRES, username="varasto",
                             password="testi", dbname="varasto",
                             driver="psycopg")
# @loppu postgres


def redis_kontti() -> RedisContainer:
    return RedisContainer(kuvat.REDIS)


# @alku apukuva
def apukuva() -> DockerImage:
    """Rakentaa apupalvelujen kuvan hakemistosta apukuva/.

    Docker käyttää välimuistia, joten toinen rakennus kestää hetken."""
    return DockerImage(path=APUKUVAN_LAHDE, tag=kuvat.APUKUVA,
                       clean_up=False)


def hintapalvelu(rajapinta: str = "1") -> DockerContainer:
    """Hintapalvelun väärennös. Valmis, kun /terveys vastaa 200."""
    return (DockerContainer(kuvat.APUKUVA)
            .with_env("RAJAPINTA", rajapinta)
            .with_exposed_ports(8080)
            .waiting_for(HttpWaitStrategy(8080, "/terveys")
                         .for_status_code(200)))
# @loppu apukuva


# @alku vikaproxy
def vikaproxy(verkko: Network, kohde: str) -> DockerContainer:
    """TCP-välityspalvelin kohteeseen 'isäntä:portti' samassa
    Docker-verkossa. Data kulkee portin 8666 kautta, ohjaus 8474."""
    return (DockerContainer(kuvat.APUKUVA)
            .with_command(["python3", "-u", "vikaproxy.py"])
            .with_env("KOHDE", kohde)
            .with_network(verkko)
            .with_exposed_ports(8666, 8474)
            .waiting_for(LogMessageWaitStrategy("vikaproxy valmis")))
# @loppu vikaproxy


def osoite(kontti: DockerContainer, portti: int) -> str:
    """Kontin portti isännältä katsottuna, esim. 'http://127.0.0.1:32768'."""
    isanta = kontti.get_container_host_ip()
    return f"http://{isanta}:{kontti.get_exposed_port(portti)}"
