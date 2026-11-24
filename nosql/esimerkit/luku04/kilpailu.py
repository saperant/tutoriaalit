"""Kadonnut päivitys ja kaksi tapaa estää se."""

import redis

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    r = ymp.redis()
    r.flushall()
    isanta, portti = ymp.osoite("redis", 6379)
    toinen = redis.Redis(host=isanta, port=portti, decode_responses=True)

    # @alku kadonnut
    r.set("varasto:42", 10)
    a = int(r.get("varasto:42"))        # asiakas A lukee 10
    b = int(toinen.get("varasto:42"))   # asiakas B lukee 10
    r.set("varasto:42", a - 1)          # A myy yhden
    toinen.set("varasto:42", b - 1)     # B myy yhden
    print("kaksi myyntia, varasto:", r.get("varasto:42"))
    # @loppu kadonnut

    # @alku atominen
    r.set("varasto:42", 10)
    r.decr("varasto:42")
    toinen.decr("varasto:42")
    print("DECR, varasto:", r.get("varasto:42"))
    # @loppu atominen

    # @alku watch
    r.set("varasto:42", 1)
    with r.pipeline() as putki:
        putki.watch("varasto:42")        # optimistinen lukko
        maara = int(putki.get("varasto:42"))
        toinen.decr("varasto:42")        # B ehtii väliin
        putki.multi()
        putki.set("varasto:42", maara - 1)
        try:
            putki.execute()
            print("A: myynti onnistui")
        except redis.WatchError:
            print("A: EXEC hylattiin, avain muuttui")
    print("varasto:", r.get("varasto:42"))
    # @loppu watch
    toinen.close()


if __name__ == "__main__":
    aja(ajo)
