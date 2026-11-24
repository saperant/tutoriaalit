"""Vientityökalun tarkistealgoritmi Pythonilla, purun perusteella.

Käyttö:
  python3 tarkiste.py laske TEKSTI...    tulostaa tarkisteet
  python3 tarkiste.py vertaa OHJELMA     vertaa ohjelmaan 2000 rivillä

Purku näyttää kaksi summaa, jotka lasketaan modulo 251 (0xfb;
jakolasku on toteutettu kertolaskuna, ks. luku 5): a alkaa ykkösestä ja
kasvaa tavulla, b kasvaa a:lla. Tulos on (b << 8 | a) XOR 0x5a5a
(Fletcherin tarkisteen muunnelma).
"""

import random
import string
import subprocess
import sys


# @alku tarkiste
def tarkiste(data: bytes) -> int:
    a, b = 1, 0
    for tavu in data:
        a = (a + tavu) % 251
        b = (b + a) % 251
    return ((b << 8) | a) ^ 0x5A5A
# @loppu tarkiste


def vertaa(ohjelma: str) -> None:
    """Eroavuustesti: samat satunnaiset rivit ohjelmalle ja mallille."""
    satunnainen = random.Random(251)
    merkit = string.ascii_letters + string.digits + " .,-_"
    rivit = ["", "a", "lampo 21.5"]
    rivit += ["".join(satunnainen.choices(merkit, k=satunnainen.randint(
        1, 200))) for _ in range(2000)]
    tuloste = subprocess.run([ohjelma], input="\n".join(rivit) + "\n",
                             check=True, capture_output=True,
                             text=True).stdout.splitlines()
    erot = sum(1 for rivi, saatu in zip(rivit, tuloste, strict=True)
               if saatu != f"{tarkiste(rivi.encode()):04x} {rivi}")
    print(f"{len(rivit)} riviä, eroja {erot}")


def main() -> None:
    if sys.argv[1] == "laske":
        for teksti in sys.argv[2:]:
            print(f"{tarkiste(teksti.encode()):04x} {teksti}")
    else:
        vertaa(sys.argv[2])


if __name__ == "__main__":
    main()
