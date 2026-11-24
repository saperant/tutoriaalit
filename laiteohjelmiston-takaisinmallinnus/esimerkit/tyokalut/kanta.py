"""Raa'an kuvan latausosoitteen päättely osoittimista.

Käyttö: python3 kanta.py KUVA [ALKU LOPPU ASKEL]

Jokaiselle ehdokasosoitteelle lasketaan, moneenko eri merkkijonon
alkuun kuvan sanat osoittavat, jos kuva ladataan siihen. Oikealla
kannalla literaalivarantojen merkkijono-osoittimet osuvat, väärällä
eivät. Kukin kohde lasketaan vain kerran, koska sama arvo voi toistua
(esim. vektoritaulun oletuskäsittelijä).
"""
import sys

from kuva import Kuva


# @alku pisteet
def pisteet(data: bytes, kanta: int) -> int:
    kuva = Kuva(data, kanta)
    osumat = set()
    for _, arvo in kuva.sanat(kanta, kuva.loppu):
        if kuva.sisaltaa(arvo) and arvo != kanta:
            teksti = kuva.merkkijono(arvo)
            edellinen = kuva.tavut(arvo - 1, 1) if arvo > kanta else b"\0"
            if teksti and len(teksti) >= 4 and edellinen == b"\0":
                osumat.add(arvo)
    return len(osumat)
# @loppu pisteet


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    alku, loppu, askel = 0, 0x40000, 0x100
    if len(sys.argv) > 4:
        alku, loppu, askel = (int(a, 0) for a in sys.argv[2:5])
    tulokset = sorted(((pisteet(data, k), k)
                       for k in range(alku, loppu, askel)), reverse=True)
    for osumia, kanta in tulokset[:4]:
        print(f"kanta {kanta:#07x}: {osumia} merkkijono-osoitinta")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
