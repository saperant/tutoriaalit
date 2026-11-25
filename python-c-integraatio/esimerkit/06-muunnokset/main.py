"""Kopio vai viite: pybind11:n automaattiset muunnokset, läpinäkymättömät
tyypit, elinaikojen sitominen ja Python-koodi C++:n kutsumana."""

import gc

import muunnos
import takaisin


# @alku periva
class Kaksinkertaistaja(takaisin.Suodin):
    """C++-rajapinnan toteutus Pythonilla."""

    def kasittele(self, x: float) -> float:
        return 2.0 * x


class Puutteellinen(takaisin.Suodin):
    """Ei määrittele metodia kasittele."""
# @loppu periva


def kaatuva(x: float) -> None:
    raise ValueError(f"liian suuri arvo: {x}")


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

    # @alku takaisinkutsu
    halytin = takaisin.Halytin(raja=10.0)
    ylitykset: list[float] = []
    halytin.kun_ylittyy(ylitykset.append)    # C++ pitää viitteen elossa
    print("ylityksiä:", halytin.syota([3.0, 12.0, 7.0, 15.0]), ylitykset)

    halytin.kun_ylittyy(kaatuva)
    try:
        halytin.syota([11.0])
    except ValueError as virhe:
        print("poikkeus kulki C++:n läpi:", virhe)
    # @loppu takaisinkutsu

    # @alku trampoliini
    print("suodatettu summa:",
          takaisin.summa_suodatettuna(Kaksinkertaistaja(), [1.0, 2.0, 3.0]))
    try:
        takaisin.summa_suodatettuna(Puutteellinen(), [1.0])
    except RuntimeError as virhe:
        print("puuttuva metodi:", virhe)
    # @loppu trampoliini


if __name__ == "__main__":
    main()
