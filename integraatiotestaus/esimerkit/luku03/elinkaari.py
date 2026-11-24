"""Kontin elinkaari ilman with-lausetta: käynnistys, odotus, käyttö,
pysäytys. Tulostaa vain asiat, jotka eivät vaihdu ajosta toiseen."""

from __future__ import annotations

import redis
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from testiapu import kuvat


# @alku elinkaari
def main() -> None:
    kontti = (DockerContainer(kuvat.REDIS)
              .with_exposed_ports(6379)
              .waiting_for(LogMessageWaitStrategy(
                  "Ready to accept connections")))
    kontti.start()              # luo, käynnistää ja odottaa valmiutta
    try:
        isanta = kontti.get_container_host_ip()
        portti = int(kontti.get_exposed_port(6379))
        print("tila:", kontti.status)
        print("isäntäportti satunnainen:", portti != 6379)
        r = redis.Redis(host=isanta, port=portti)
        r.set("tervehdys", "hei")
        print("arvo:", r.get("tervehdys"))
        r.close()
    finally:
        tunnus = kontti.get_wrapped_container().id
        kontti.stop()           # pysäyttää ja poistaa kontin
    jaljella = kontti.get_docker_client().client.containers.list(
        all=True, filters={"id": tunnus})
    print("kontti poistettu:", jaljella == [])
# @loppu elinkaari


if __name__ == "__main__":
    main()
