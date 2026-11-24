"""Intel HEX -tiedoston tietueiden tarkistus ja yhteenveto.

Käyttö: python3 ihex.py TIEDOSTO.hex

Tietue on muotoa :LLAAAATT<data>CC, jossa LL on datan pituus, AAAA
osoitteen alaosa, TT tyyppi ja CC tarkiste (tavujen summan kahden
komplementti).
"""
import sys
from collections import Counter

TYYPIT = {0: "data", 1: "loppu", 2: "segmentti", 3: "aloitus CS:IP",
          4: "osoitteen yläosa", 5: "aloitusosoite"}


# @alku tietue
def tietue(rivi: str) -> tuple[int, int, bytes]:
    """Palauttaa (tyyppi, osoite, data); tarkiste tarkistetaan."""
    tavut = bytes.fromhex(rivi[1:])
    if sum(tavut) & 0xFF != 0:
        raise ValueError(f"väärä tarkiste: {rivi}")
    pituus, osoite, tyyppi = tavut[0], tavut[1] << 8 | tavut[2], tavut[3]
    return tyyppi, osoite, tavut[4:4 + pituus]
# @loppu tietue


def main() -> None:
    ylaosa = 0
    tyypit: Counter[int] = Counter()
    alku, loppu, tavuja = 1 << 32, 0, 0
    with open(sys.argv[1]) as f:
        for rivi in f:
            tyyppi, osoite, data = tietue(rivi.strip())
            tyypit[tyyppi] += 1
            if tyyppi == 2:        # segmentti: osoite = arvo * 16
                ylaosa = int.from_bytes(data, "big") << 4
            elif tyyppi == 4:      # 32-bittisen osoitteen yläosa
                ylaosa = int.from_bytes(data, "big") << 16
            elif tyyppi == 0:
                alku = min(alku, ylaosa + osoite)
                loppu = max(loppu, ylaosa + osoite + len(data))
                tavuja += len(data)
            elif tyyppi in (3, 5):
                print(f"aloitusosoite {int.from_bytes(data, 'big'):#x}")
    for tyyppi, maara in sorted(tyypit.items()):
        print(f"tyyppi {tyyppi:02x} ({TYYPIT.get(tyyppi, '?')}): {maara}")
    print(f"data {tavuja} tavua, osoitteet {alku:#x}..{loppu:#x}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
