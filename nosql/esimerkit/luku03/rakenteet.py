"""Redisin tietorakenteet verkkokaupan tarpeisiin."""

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    r = ymp.redis()
    r.flushall()

    # @alku merkkijonot
    r.set("tuote:42:nimi", "Retkikeitin")
    r.set("tuote:42:varasto", 5)
    r.incrby("tuote:42:varasto", 10)     # atominen lisäys palvelimella
    r.decr("tuote:42:varasto")
    print("varasto:", r.get("tuote:42:varasto"))
    # @loppu merkkijonot

    # @alku hajautus
    r.hset("kayttaja:7", mapping={"nimi": "Aino", "kaupunki": "Oulu",
                                  "tilauksia": 0})
    r.hincrby("kayttaja:7", "tilauksia", 1)
    print("kayttaja:", sorted(r.hgetall("kayttaja:7").items()))
    # @loppu hajautus

    # @alku lista
    for tapahtuma in ["katsoi:42", "katsoi:17", "osti:42", "katsoi:99"]:
        r.lpush("historia:7", tapahtuma)
        r.ltrim("historia:7", 0, 2)      # vain kolme uusinta
    print("historia:", r.lrange("historia:7", 0, -1))
    # @loppu lista

    # @alku joukko
    r.sadd("tuote:42:tagit", "retkeily", "keittio", "kevyt")
    r.sadd("tuote:17:tagit", "retkeily", "valaisin", "kevyt")
    print("yhteiset tagit:", sorted(r.sinter("tuote:42:tagit",
                                             "tuote:17:tagit")))
    # @loppu joukko

    # @alku jarjestetty
    myynnit = {"retkikeitin": 120, "otsalamppu": 340, "makuupussi": 95,
               "teltta": 210}
    r.zadd("myynti:viikko", myynnit)
    r.zincrby("myynti:viikko", 150, "makuupussi")
    for sija, (tuote, kpl) in enumerate(
            r.zrevrange("myynti:viikko", 0, 2, withscores=True), start=1):
        print(f"{sija}. {tuote} {int(kpl)}")
    print("teltan sija (0 = paras):",
          r.zrevrank("myynti:viikko", "teltta"))
    # @loppu jarjestetty


if __name__ == "__main__":
    aja(ajo)
