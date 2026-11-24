"""Korrelaatiotehoanalyysi (CPA) simuloiduilla virrankulutusmittauksilla.

Suoritin kuluttaa sitä enemmän virtaa, mitä useampi väylän bitti on
ykkönen (Hammingin paino). Kun laite laskee AES:n ensimmäisen kierroksen
S-laatikon tuloksen S[p XOR k], mittaus vuotaa sen painon. Hyökkääjä
tuntee syötteet p, kokeilee kaikki 256 avaintavun arvausta ja valitsee
sen, jonka ennuste korreloi mittausten kanssa parhaiten. Maskattu
toteutus käsittelee arvoa S[p XOR k] XOR m satunnaisella maskilla m,
jolloin yksittäinen mittaus ei korreloi minkään arvauksen kanssa.
"""

import random
from statistics import correlation


# @alku sbox
def aes_sbox() -> list[int]:
    """AES:n S-laatikko: käänteisalkio GF(2^8):ssa ja affiinimuunnos."""
    def kerro(a: int, b: int) -> int:
        tulos = 0
        while b:
            if b & 1:
                tulos ^= a
            a = ((a << 1) ^ (0x1B if a & 0x80 else 0)) & 0xFF
            b >>= 1
        return tulos

    def kaanteis(a: int) -> int:     # a^254 = a^-1, ja 0 -> 0
        tulos = 1
        for _ in range(254):
            tulos = kerro(tulos, a)
        return tulos if a else 0

    def kierra(x: int, n: int) -> int:
        return ((x << n) | (x >> (8 - n))) & 0xFF

    return [kaanteis(a) ^ kierra(kaanteis(a), 1) ^ kierra(kaanteis(a), 2)
            ^ kierra(kaanteis(a), 3) ^ kierra(kaanteis(a), 4) ^ 0x63
            for a in range(256)]
# @loppu sbox


SBOX = aes_sbox()


def paino(x: int) -> int:
    return x.bit_count()


# @alku mittaa
def mittaa(avain: int, syotteet: list[int], maskattu: bool,
           kohina: random.Random) -> list[float]:
    """Yksi mittauspiste suoritusta kohden: vuoto + mittauskohina."""
    tulos = []
    for p in syotteet:
        arvo = SBOX[p ^ avain]
        if maskattu:
            arvo ^= kohina.getrandbits(8)    # uusi maski joka kerta
        tulos.append(paino(arvo) + kohina.gauss(0, 2.0))
    return tulos


def hyokkaa(syotteet: list[int], mittaukset: list[float]) -> int:
    """Arvaus, jonka ennuste korreloi mittausten kanssa eniten."""
    def osuvuus(arvaus: int) -> float:
        ennuste = [float(paino(SBOX[p ^ arvaus])) for p in syotteet]
        return abs(correlation(ennuste, mittaukset))
    return max(range(256), key=osuvuus)
# @loppu mittaa


def main() -> None:
    assert SBOX[0x00] == 0x63 and SBOX[0x53] == 0xED   # FIPS 197
    avain = 0x2B
    satunnainen = random.Random(7)
    for maskattu in (False, True):
        nimi = "Maskattu   " if maskattu else "Maskaamaton"
        rivit = []
        for n in (20, 100, 2000):
            syotteet = [satunnainen.getrandbits(8) for _ in range(n)]
            mitat = mittaa(avain, syotteet, maskattu, satunnainen)
            arvaus = hyokkaa(syotteet, mitat)
            rivit.append(f"{n} mittausta: "
                         f"{'oikein' if arvaus == avain else 'väärin'}")
        print(f"{nimi}  " + ", ".join(rivit))


if __name__ == "__main__":
    main()
