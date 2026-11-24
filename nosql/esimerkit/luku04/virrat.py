"""Redis Streams: tilaustapahtumat kuluttajaryhmälle."""

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    r = ymp.redis()
    r.flushall()
    # @alku tuottaja
    for tilaus in ["T1", "T2", "T3", "T4"]:
        r.xadd("tilaukset", {"tilaus": tilaus, "tila": "luotu"})
    r.xgroup_create("tilaukset", "laskutus", id="0")
    # @loppu tuottaja

    # @alku kuluttajat
    def lue(kuluttaja: str, maara: int) -> list[tuple[str, str]]:
        vastaus = r.xreadgroup("laskutus", kuluttaja,
                               {"tilaukset": ">"}, count=maara)
        return [(id_, kentat["tilaus"]) for id_, kentat in vastaus[0][1]]

    viestit_a = lue("a", 2)
    viestit_b = lue("b", 2)
    print("a sai:", [t for _, t in viestit_a])
    print("b sai:", [t for _, t in viestit_b])
    r.xack("tilaukset", "laskutus", *[i for i, _ in viestit_a])
    # b kaatuu kuittaamatta: viestit jäävät odottamaan.
    odottaa = r.xpending("tilaukset", "laskutus")
    print("kuittaamatta:", odottaa["pending"],
          "kuluttajalla:", [k["name"] for k in odottaa["consumers"]])
    # @loppu kuluttajat

    # @alku siirto
    siirretyt = r.xautoclaim("tilaukset", "laskutus", "a",
                             min_idle_time=0, start_id="0")
    print("a otti haltuun:", [k["tilaus"] for _, k in siirretyt[1]])
    r.xack("tilaukset", "laskutus", *[i for i, _ in siirretyt[1]])
    print("kuittaamatta:",
          r.xpending("tilaukset", "laskutus")["pending"])
    # @loppu siirto


if __name__ == "__main__":
    aja(ajo)
