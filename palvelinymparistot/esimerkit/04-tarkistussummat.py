"""Hiljainen datan korruptoituminen ja tarkistussummat.

Tavallinen peili (RAID 1) lukee kumman tahansa kopion. Jos toisen
levyn sektori on vioittunut ilman lukuvirhettä (bittimätä), peili ei
tiedä, kumpi kopio on oikea. ZFS ja Btrfs tallentavat jokaisen lohkon
tarkistussumman erilleen lohkosta, joten ne tunnistavat oikean kopion
ja korjaavat väärän. Läpikäynti (scrub) lukee kaiken ja korjaa viat
ennen kuin niitä tarvitaan.
"""

import hashlib


def summa(lohko: bytes) -> bytes:
    return hashlib.sha256(lohko).digest()


# @alku peili
class TarkistettuPeili:
    def __init__(self, lohkot: list[bytes]) -> None:
        self.kopiot = [list(lohkot), list(lohkot)]
        self.summat = [summa(b) for b in lohkot]  # erillään datasta

    def lue(self, i: int) -> bytes:
        for kopio in self.kopiot:
            if summa(kopio[i]) == self.summat[i]:
                self.korjaa(i, kopio[i])
                return kopio[i]
        raise OSError(f"lohko {i}: molemmat kopiot vioittuneet")

    def korjaa(self, i: int, oikea: bytes) -> None:
        for kopio in self.kopiot:
            if kopio[i] != oikea:
                kopio[i] = oikea   # itsekorjaus (self-healing)

    def lapikaynti(self) -> int:
        """scrub: lukee kaikki lohkot ja palauttaa korjausten määrän."""
        viallisia = 0
        for i, oikea_summa in enumerate(self.summat):
            if any(summa(k[i]) != oikea_summa for k in self.kopiot):
                viallisia += 1
                self.lue(i)
        return viallisia
# @loppu peili


def main() -> None:
    # @alku koe
    lohkot = [f"tilaus {n:04}".encode() for n in range(6)]
    peili = TarkistettuPeili(lohkot)
    peili.kopiot[0][2] = b"tilaus 9999"    # bittimätä levyllä 0
    peili.kopiot[1][4] = b"tilaus 0000"    # ja levyllä 1
    print("lohko 2 luettuna:", peili.lue(2).decode())
    print("läpikäynti korjasi:", peili.lapikaynti(), "lohkoa")
    print("läpikäynti uudelleen:", peili.lapikaynti(), "lohkoa")
    peili.kopiot[0][5] = peili.kopiot[1][5] = b"rikki"
    try:
        peili.lue(5)
    except OSError as virhe:
        print("virhe:", virhe)
    # @loppu koe


if __name__ == "__main__":
    main()
