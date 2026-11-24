"""Redisin asynkroninen replikointi ja WAIT."""

import redis

from nosql.kontit import erillinen, odota

KOMENTO = ("sh -c 'redis-server --port 6380 --replicaof 127.0.0.1 6379"
           " --daemonize yes && exec redis-server --port 6379'")


def ajo(_ymp: object) -> None:
    with erillinen("redis", KOMENTO, 6379, 6380) as kontti:
        isanta = kontti.get_container_host_ip()

        def yhteys(portti: int) -> redis.Redis:
            r = redis.Redis(host=isanta,
                            port=int(kontti.get_exposed_port(portti)),
                            decode_responses=True)
            r.ping()
            return r

        ensi = odota(lambda: yhteys(6379))
        replika = odota(lambda: yhteys(6380))

        def yhdistetty() -> None:
            # Replika on käytössä vasta, kun alkusynkronointi on valmis.
            tila = ensi.info("replication").get("slave0", {})
            if tila.get("state") != "online":
                raise RuntimeError("replika ei vielä valmis")
        odota(yhdistetty)

        # @alku wait
        ensi.set("kori:7", "42,17")
        kuittasi = ensi.wait(1, 1000)       # odota 1 replikaa, max 1 s
        print("replikoita kuittasi:", kuittasi)
        print("replikalta:", replika.get("kori:7"))
        # @loppu wait

        # @alku vain-luku
        try:
            replika.set("kori:7", "99")
        except redis.ResponseError as virhe:
            print("kirjoitus replikaan:", type(virhe).__name__)
        print("rooli:", replika.info("replication")["role"])
        # @loppu vain-luku
        ensi.close()
        replika.close()


if __name__ == "__main__":
    ajo(None)
