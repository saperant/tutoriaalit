"""Välimuistiryntäys (cache stampede) ja sen esto vuokralla.

Suosittu avain vanhenee, ja 20 pyyntöä saapuu samalla hetkellä.
Kannasta haku kestää 300 ms. Ilman suojaa jokainen pyyntö toteaa
hudin ja kysyy kannalta itse; vuokran kanssa yksi hakee ja muut
odottavat sen tulosta.
"""

import threading
from collections.abc import Callable

from jarjestelma.resp import Redis
from jarjestelma.valimuisti import (
    Tietokanta,
    hae_rinnalta,
    hae_vuokralla,
    invalidoi,
)
from jarjestelma.ymparisto import Ymparisto

PYYNTOJA = 20


# @alku ryntays
def ryntays(portti: int, hae: Callable[[Redis], str]) -> list[str]:
    tulokset: list[str] = []
    lahto = threading.Barrier(PYYNTOJA)

    def pyynto() -> None:
        with Redis(portti) as r:
            lahto.wait()              # kaikki liikkeelle yhtä aikaa
            arvo = hae(r)
        tulokset.append(arvo)

    saikeet = [threading.Thread(target=pyynto) for _ in range(PYYNTOJA)]
    for s in saikeet:
        s.start()
    for s in saikeet:
        s.join()
    return tulokset
# @loppu ryntays


def main() -> None:
    kanta = Tietokanta({"etusivu": "<html>...</html>"}, viive=0.3)
    with Ymparisto() as ymp:
        portti = ymp.redis()
        for nimi, hae in [
                ("ilman suojaa", lambda r: hae_rinnalta(r, kanta, "etusivu")),
                ("vuokralla", lambda r: hae_vuokralla(r, kanta, "etusivu"))]:
            with Redis(portti) as r:
                invalidoi(r, "etusivu")
            ennen = kanta.hakuja
            tulokset = ryntays(portti, hae)
            haut = kanta.hakuja - ennen
            kuvaus = "1" if haut == 1 else "useita" if haut > 1 else "0"
            print(f"{nimi}: {len(tulokset)} vastausta,"
                  f" kantahakuja {kuvaus}")


if __name__ == "__main__":
    main()
