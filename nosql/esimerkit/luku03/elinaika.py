"""Istunnot ja elinaika (TTL)."""

import time
import uuid

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    r = ymp.redis()
    r.flushall()

    # @alku istunto
    tunnus = uuid.uuid4().hex
    avain = f"istunto:{tunnus}"
    r.hset(avain, mapping={"kayttaja": "7", "kori": "42,17"})
    r.expire(avain, 1800)            # 30 minuuttia käyttämättä
    print("elinaika yli 29 min:", r.ttl(avain) > 29 * 60)
    # Jokainen pyyntö jatkaa istuntoa (liukuva elinaika).
    r.expire(avain, 1800)
    # @loppu istunto

    # @alku vanheneminen
    r.set("tarjous:kesa", "-20 %", px=300)    # 300 ms
    print("heti:", r.get("tarjous:kesa"))
    time.sleep(0.6)
    print("0,6 s kuluttua:", r.get("tarjous:kesa"))
    print("ttl puuttuvalle avaimelle:", r.ttl("tuote:ei-ole"))
    r.persist(avain)                  # elinaika pois
    print("ttl pysyvalle avaimelle:", r.ttl(avain))
    # @loppu vanheneminen


if __name__ == "__main__":
    aja(ajo)
