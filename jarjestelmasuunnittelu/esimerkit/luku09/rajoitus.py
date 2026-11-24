"""Nopeusrajoitus: token bucket yhdellä palvelimella ja koko klusterissa.

Asiakkaalle sallitaan 5 pyyntöä sekunnissa ja 10 pyynnön purske.
Ensin sanko simuloidulla kellolla, sitten sama raja Redisissä, kun
kolme palvelininstanssia jakaa kuorman. Jos jokaisella instanssilla
on oma paikallinen sanko, asiakas saa kolminkertaisen rajan.
"""

from jarjestelma.rajoitin import SANKO_LUA, Sanko
from jarjestelma.resp import Redis, luku, teksti
from jarjestelma.ymparisto import Ymparisto


class Kello:
    def __init__(self) -> None:
        self.aika = 0.0

    def __call__(self) -> float:
        return self.aika


def main() -> None:
    # @alku paikallinen
    kello = Kello()
    sanko = Sanko(nopeus=5, koko=10, kello=kello)
    purske = sum(sanko.salli() for _ in range(20))
    print(f"t=0.0 s: 20 pyyntöä kerralla, sallittiin {purske}")
    kello.aika = 1.0
    print(f"t=1.0 s: 20 pyyntöä kerralla, sallittiin"
          f" {sum(sanko.salli() for _ in range(20))}")
    sallitut = 0
    for i in range(100):                 # 10 pyyntöä/s 10 sekunnin ajan
        kello.aika = 2.0 + i / 10
        sallitut += sanko.salli()
    print(f"t=2-12 s: 10 pyyntöä/s, sallittiin {sallitut}/100")
    # @loppu paikallinen

    with Ymparisto() as ymp:
        portti = ymp.redis()
        instanssit = [Redis(portti) for _ in range(3)]
        # @alku jaettu
        sha = teksti(instanssit[0].komento("SCRIPT", "LOAD", SANKO_LUA))
        sallittu = 0
        for i in range(30):              # kuormantasaaja jakaa kierrossa
            r = instanssit[i % 3]
            sallittu += luku(r.komento("EVALSHA", sha, 1,
                                       "raja:asiakas-42", 0.001, 10))
        # @loppu jaettu
        print(f"jaettu raja Redisissä, 30 pyyntöä 3 instanssiin:"
              f" sallittiin {sallittu}")
        paikalliset = [Sanko(0.001, 10, kello) for _ in range(3)]
        erikseen = sum(paikalliset[i % 3].salli() for i in range(30))
        print(f"paikalliset rajat, 30 pyyntöä 3 instanssiin:"
              f" sallittiin {erikseen}")
        for r in instanssit:
            r.close()


if __name__ == "__main__":
    main()
