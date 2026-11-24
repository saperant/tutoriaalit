"""Tietokannat konteissa esimerkkejä ja testejä varten.

Ymparisto käynnistää kunkin tietokannan vasta, kun sitä pyydetään, ja
pitää sen käynnissä, kunnes ympäristö suljetaan. Pytest-ajossa kaikki
esimerkit käyttävät samaa ympäristöä (testit/conftest.py), joten
esimerkiksi Cassandra käynnistyy vain kerran. Yksittäinen esimerkki
käynnistää oman ympäristönsä:

    python3 luku03/rakenteet.py

Kontit käynnistää Testcontainers. Kuvien versiot on lukittu, ja ne
haetaan Docker Hubin kuvien Google-peilistä, koska Docker Hub
rajoittaa nimettömiä latauksia. Peilin voi vaihtaa muuttujalla
NOSQL_PEILI (esim. tyhjäksi, jolloin kuvat tulevat Docker Hubista).
"""

from __future__ import annotations

import contextlib
import logging
import os
import time
from collections.abc import Callable, Iterator
from typing import Any

import neo4j
import psycopg
import pymongo
import redis
from cassandra.cluster import Cluster, Session
from cassandra.policies import AddressTranslator
from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer

# @alku kuvat
PEILI = os.environ.get("NOSQL_PEILI", "mirror.gcr.io/")
KUVAT = {
    "redis": PEILI + "library/redis:7.2-alpine",
    "mongo": PEILI + "library/mongo:8.0.38",
    "cassandra": PEILI + "library/cassandra:5.0.9",
    "neo4j": PEILI + "library/neo4j:5.26.34-community",
    "postgres": PEILI + "library/postgres:16.11-alpine",
}
# Siivoojakontti (Ryuk) poistaa kontit, jos ajo kaatuu kesken.
testcontainers_config.ryuk_image = PEILI + "testcontainers/ryuk:0.8.1"
# @loppu kuvat

# Cassandra-ajuri kirjoittaa varoituksia esim. protokollaversion
# neuvottelusta; esimerkkien tuloste pidetään puhtaana.
logging.getLogger("cassandra").setLevel(logging.ERROR)


def odota[T](yritys: Callable[[], T], aikaraja: float = 120.0) -> T:
    """Kutsuu funktiota, kunnes se onnistuu tai aikaraja täyttyy."""
    loppu = time.monotonic() + aikaraja
    while True:
        try:
            return yritys()
        except Exception:
            if time.monotonic() > loppu:
                raise
            time.sleep(0.5)


class KaikkiSamaan(AddressTranslator):  # type: ignore[misc]
    """Cassandra kertoo asiakkaalle kontin sisäisen osoitteen; asiakas
    ohjataan aina julkaistuun osoitteeseen."""

    def __init__(self, isanta: str) -> None:
        self.isanta = isanta

    def translate(self, addr: str) -> str:
        return self.isanta


class Ymparisto:
    """Laiskasti käynnistyvät tietokannat ja niiden asiakkaat."""

    def __init__(self) -> None:
        self._kontit: dict[str, DockerContainer] = {}
        self._asiakkaat: dict[str, Any] = {}

    def __enter__(self) -> Ymparisto:
        return self

    def __exit__(self, *_: object) -> None:
        self.sulje()

    def sulje(self) -> None:
        for nimi, asiakas in self._asiakkaat.items():
            with contextlib.suppress(Exception):
                if nimi == "cassandra":
                    asiakas.shutdown()
                elif nimi != "cassandra-istunto":
                    asiakas.close()
        for kontti in self._kontit.values():
            with contextlib.suppress(Exception):
                kontti.stop()
        self._asiakkaat.clear()
        self._kontit.clear()

    def _kaynnista(self, nimi: str, kontti: DockerContainer) -> None:
        kontti.start()
        self._kontit[nimi] = kontti

    def osoite(self, nimi: str, portti: int) -> tuple[str, int]:
        kontti = self._kontit[nimi]
        return (kontti.get_container_host_ip(),
                int(kontti.get_exposed_port(portti)))

    # @alku redis
    def redis(self) -> redis.Redis:
        if "redis" not in self._asiakkaat:
            self._kaynnista("redis", DockerContainer(
                KUVAT["redis"]).with_exposed_ports(6379))
            isanta, portti = self.osoite("redis", 6379)
            asiakas = redis.Redis(host=isanta, port=portti,
                                  decode_responses=True)
            odota(asiakas.ping)
            self._asiakkaat["redis"] = asiakas
        r: redis.Redis = self._asiakkaat["redis"]
        return r
    # @loppu redis

    def mongo(self) -> pymongo.MongoClient[dict[str, Any]]:
        if "mongo" not in self._asiakkaat:
            # Transaktiot vaativat replikajoukon, joten yksikin solmu
            # käynnistetään yhden jäsenen replikajoukkona.
            self._kaynnista("mongo", DockerContainer(KUVAT["mongo"])
                            .with_command("--replSet rs0 --bind_ip_all")
                            .with_exposed_ports(27017))
            isanta, portti = self.osoite("mongo", 27017)
            asiakas: pymongo.MongoClient[dict[str, Any]] = (
                pymongo.MongoClient(isanta, portti, directConnection=True,
                                    serverSelectionTimeoutMS=2000))
            odota(lambda: asiakas.admin.command("ping"))
            asiakas.admin.command("replSetInitiate", {
                "_id": "rs0",
                "members": [{"_id": 0, "host": "localhost:27017"}]})

            def ensisijainen() -> None:
                if not asiakas.admin.command("hello")["isWritablePrimary"]:
                    raise RuntimeError("ei vielä ensisijainen")
            odota(ensisijainen)
            # Asiakas näki palvelimen ennen replikajoukon alustusta
            # (ei istuntoja eikä transaktioita): uusi yhteys.
            asiakas.close()
            asiakas = pymongo.MongoClient(isanta, portti,
                                          directConnection=True)
            odota(lambda: asiakas.admin.command("ping"))
            self._asiakkaat["mongo"] = asiakas
        m: pymongo.MongoClient[dict[str, Any]] = self._asiakkaat["mongo"]
        return m

    def cassandra(self) -> Session:
        if "cassandra" not in self._asiakkaat:
            # Pieni muisti ja yksi poletti: yksi solmu käynnistyy
            # nopeammin eikä vie koko konetta.
            self._kaynnista("cassandra", DockerContainer(KUVAT["cassandra"])
                            .with_env("MAX_HEAP_SIZE", "512M")
                            .with_env("HEAP_NEWSIZE", "128M")
                            .with_env("JVM_EXTRA_OPTS",
                                      "-Dcassandra.skip_wait_for_gossip"
                                      "_to_settle=0 -Dcassandra.num_tokens=1"
                                      " -Dcassandra.initial_token=0")
                            .with_exposed_ports(9042))
            isanta, portti = self.osoite("cassandra", 9042)

            def yhdista() -> tuple[Cluster, Session]:
                # Epäonnistunut yhteys sulkee Cluster-olion, joten
                # jokainen yritys tekee uuden.
                klusteri = Cluster([isanta], port=portti,
                                   address_translator=KaikkiSamaan(isanta),
                                   protocol_version=5, connect_timeout=20,
                                   control_connection_timeout=20)
                try:
                    istunto = klusteri.connect()
                    istunto.default_timeout = 60
                    # Juuri käynnistynyt solmu voi vielä hylätä kyselyjä.
                    istunto.execute("SELECT now() FROM system.local")
                    return klusteri, istunto
                except Exception:
                    klusteri.shutdown()
                    raise
            klusteri, istunto = odota(yhdista, aikaraja=240)
            self._asiakkaat["cassandra"] = klusteri
            self._asiakkaat["cassandra-istunto"] = istunto
        s: Session = self._asiakkaat["cassandra-istunto"]
        return s

    def neo4j(self) -> neo4j.Driver:
        if "neo4j" not in self._asiakkaat:
            self._kaynnista("neo4j", DockerContainer(KUVAT["neo4j"])
                            .with_env("NEO4J_AUTH", "none")
                            .with_env("NEO4J_server_memory_heap_max__size",
                                      "512m")
                            .with_env("NEO4J_server_memory_pagecache_size",
                                      "64m")
                            .with_exposed_ports(7687))
            isanta, portti = self.osoite("neo4j", 7687)
            ajuri = neo4j.GraphDatabase.driver(f"bolt://{isanta}:{portti}")
            odota(ajuri.verify_connectivity)
            self._asiakkaat["neo4j"] = ajuri
        d: neo4j.Driver = self._asiakkaat["neo4j"]
        return d

    def postgres(self) -> psycopg.Connection[tuple[Any, ...]]:
        if "postgres" not in self._asiakkaat:
            self._kaynnista("postgres", DockerContainer(KUVAT["postgres"])
                            .with_env("POSTGRES_PASSWORD", "salasana")
                            .with_exposed_ports(5432))
            isanta, portti = self.osoite("postgres", 5432)

            def yhdista() -> psycopg.Connection[tuple[Any, ...]]:
                return psycopg.connect(
                    host=isanta, port=portti, user="postgres",
                    # Kertakäyttöisen testikontin salasana.
                    password="salasana", autocommit=True)  # noqa: S106
            self._asiakkaat["postgres"] = odota(yhdista)
        p: psycopg.Connection[tuple[Any, ...]] = self._asiakkaat["postgres"]
        return p


@contextlib.contextmanager
def erillinen(kuva: str, komento: str | None, *portit: int
              ) -> Iterator[DockerContainer]:
    """Oma kontti esimerkille, joka kaataa tai käynnistää palvelimen
    uudelleen (ei jaeta muiden esimerkkien kanssa)."""
    kontti = DockerContainer(KUVAT[kuva]).with_exposed_ports(*portit)
    if komento:
        kontti = kontti.with_command(komento)
    kontti.start()
    try:
        yield kontti
    finally:
        kontti.stop()


def aja(ajo: Callable[[Ymparisto], None]) -> None:
    """Yksittäisen esimerkin pääohjelma."""
    with Ymparisto() as ymp:
        ajo(ymp)
