"""Mitä Redisille jää, kun prosessi kuolee kesken (kill -9)?"""

import time

import redis
from testcontainers.core.container import DockerContainer

from nosql.kontit import erillinen, odota


def kokeile(kuvaus: str, komento: str, tauko: float = 0.0) -> None:
    with erillinen("redis", komento, 6379) as kontti:
        def yhteys() -> redis.Redis:
            r = redis.Redis(host=kontti.get_container_host_ip(),
                            port=int(kontti.get_exposed_port(6379)),
                            decode_responses=True)
            r.ping()
            return r

        r = odota(yhteys)
        for i in range(1000):
            r.set(f"tilaus:{i}", "maksettu")
        r.close()
        time.sleep(tauko)                # aikaa taustakirjoitukselle
        # @alku kaatuminen
        kaada_ja_kaynnista(kontti)
        # @loppu kaatuminen
        r = odota(yhteys)
        print(f"{kuvaus}: {r.dbsize()}/1000 tilausta tallessa")
        r.close()


def kaada_ja_kaynnista(kontti: DockerContainer) -> None:
    sisainen = kontti.get_wrapped_container()
    sisainen.kill(signal="SIGKILL")      # ei siistiä sammutusta
    sisainen.start()
    sisainen.reload()                    # portti voi vaihtua


def ajo(_ymp: object) -> None:
    # @alku kokeet
    kokeile("ei tallennusta", "redis-server --save '' --appendonly no")
    kokeile("RDB, save 60 1",
            "redis-server --save '60 1' --appendonly no")
    kokeile("AOF everysec, kaatuminen 1,5 s myohemmin",
            "redis-server --appendonly yes --appendfsync everysec", 1.5)
    kokeile("AOF always",
            "redis-server --appendonly yes --appendfsync always")
    # @loppu kokeet


if __name__ == "__main__":
    ajo(None)
