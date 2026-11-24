"""Tarkistaa läpinäkymättömän predikaatin: onko i * (i + 1) parillinen.

Käyttö: python3 predikaatti.py

Litistetyn funktion haara riippuu ehdosta (i * (i + 1)) mod 2 == 0,
joka lasketaan 32-bittisenä (ylivuoto pyöristää modulo 2**32). Kahdesta
peräkkäisestä kokonaisluvusta toinen on parillinen, eikä modulo 2**32
muuta tulon alinta bittiä, joten ehto on aina tosi. Skripti tarkistaa
väitteen kaikilla 16-bittisillä arvoilla, ylivuodon rajoilla ja
satunnaisotoksella.
"""

import random


def ehto(i: int) -> bool:
    tulo = (i * (i + 1)) & 0xFFFFFFFF
    return tulo % 2 == 0


def main() -> None:
    arvot = list(range(-2**15, 2**15))
    arvot += [2**31 - 1, -2**31, 2**31 - 2, 65_535, 65_536, 46_341]
    satunnainen = random.Random(7)
    arvot += [satunnainen.randrange(-2**31, 2**31) for _ in range(100_000)]
    vastaesimerkit = [i for i in arvot if not ehto(i)]
    print(f"tarkistettu {len(arvot)} arvoa, vastaesimerkkejä "
          f"{len(vastaesimerkit)}")
    if not vastaesimerkit:
        print("ehto on aina tosi: tila 0xe5013b7c on kuollutta koodia")


if __name__ == "__main__":
    main()
