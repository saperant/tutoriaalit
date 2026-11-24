"""Kuinka moni avain siirtyy, kun solmuja lisätään, ja kuinka tasaisesti
avaimet jakautuvat?

100 000 avainta neljälle solmulle, sitten viides solmu lisätään.
Ihannetapauksessa vain viidennes avaimista siirtyy uudelle solmulle,
eikä yksikään avain siirry vanhalta solmulta toiselle vanhalle.
"""

from collections import Counter
from statistics import mean

from jarjestelma.hajautus import Modulo, Rendezvous, Rengas

AVAIMET = [f"kayttaja:{i}" for i in range(100_000)]
VANHAT = ["s1", "s2", "s3", "s4"]
UUDET = [*VANHAT, "s5"]


# @alku siirto
def siirtyy(ennen: dict[str, str], jalkeen: dict[str, str]) -> str:
    siirtyneet = [a for a in AVAIMET if ennen[a] != jalkeen[a]]
    vanhalle = sum(jalkeen[a] != "s5" for a in siirtyneet)
    return (f"{len(siirtyneet) / len(AVAIMET):6.1%} siirtyy,"
            f" vanhalta vanhalle {vanhalle / len(AVAIMET):6.1%}")
# @loppu siirto


def main() -> None:
    print("Solmu lisätään (4 -> 5):")
    for nimi, tee in [("modulo", Modulo), ("rengas, 100 virt.", Rengas),
                      ("rendezvous", Rendezvous)]:
        ennen, jalkeen = tee(VANHAT), tee(UUDET)
        print(f"  {nimi:<18}" + siirtyy(
            {a: ennen.solmu(a) for a in AVAIMET},
            {a: jalkeen.solmu(a) for a in AVAIMET}))

    print("Kuormin solmu / keskiarvo, 5 solmua:")
    for virtuaaleja in (1, 10, 100, 1000):
        rengas = Rengas(UUDET, virtuaaleja)
        maarat = Counter(rengas.solmu(a) for a in AVAIMET)
        print(f"  rengas, {virtuaaleja:>4} virtuaalisolmua:"
              f" {max(maarat.values()) / mean(maarat.values()):.2f}")
    rendezvous = Rendezvous(UUDET)
    maarat = Counter(rendezvous.solmu(a) for a in AVAIMET)
    print(f"  rendezvous:                  "
          f"{max(maarat.values()) / mean(maarat.values()):.2f}")


if __name__ == "__main__":
    main()
