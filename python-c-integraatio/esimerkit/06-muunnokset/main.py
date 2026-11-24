"""Kopio vai viite: pybind11:n automaattiset muunnokset, läpinäkymättömät
tyypit ja elinaikojen sitominen."""

import gc

import muunnos


def main() -> None:
    # @alku kopio
    arvot = [1.0, 2.0, 3.0]
    muunnos.tuplaa(arvot)
    print("lista tuplauksen jälkeen:", arvot)

    laskurit = muunnos.Laskurit([1, 2, 3])
    muunnos.kasvata(laskurit)
    print("laskurit kasvatuksen jälkeen:", list(laskurit))
    # @loppu kopio

    # @alku elinaika
    ketju = muunnos.Ketju()
    ketju.lisaa(muunnos.Vahvistus(2.0))   # väliaikainen olio
    ketju.lisaa(muunnos.Vahvistus(10.0))
    gc.collect()
    print("elossa:", muunnos.Vahvistus.elossa, "| tulos:", ketju.aja(1.5))

    eka = ketju.vaihe(0)
    del ketju
    gc.collect()
    print("ketju poistettu, vaihe yhä käytössä:", eka.kasittele(4.0))
    del eka
    gc.collect()
    print("kaikki vapautettu, elossa:", muunnos.Vahvistus.elossa)
    # @loppu elinaika


if __name__ == "__main__":
    main()
