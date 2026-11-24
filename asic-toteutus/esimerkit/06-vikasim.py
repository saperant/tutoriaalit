"""Juuttumisviat, vikasimulointi ja testivektorien valinta.

Valmistusvirhe mallinnetaan juuttumisvikana (stuck-at): johdin on
pysyvästi 0 tai 1. Vikasimulointi kertoo, mitkä viat testivektorit
havaitsevat (lähtö eroaa virheettömästä piiristä). Piiri on ISCAS-85-
testipiireistä pienin, c17 (kuusi NAND-porttia).
"""

import random
from itertools import product

# @alku piiri
TULOT = ["N1", "N2", "N3", "N6", "N7"]
PORTIT = {                       # lähtö: (tulo, tulo), kaikki NAND
    "N10": ("N1", "N3"), "N11": ("N3", "N6"), "N16": ("N2", "N11"),
    "N19": ("N11", "N7"), "N22": ("N10", "N16"), "N23": ("N16", "N19"),
}
LAHDOT = ["N22", "N23"]
Vika = tuple[str, int]           # (johdin, juuttunut arvo)


def simuloi(vektori: dict[str, int], vika: Vika | None = None
            ) -> tuple[int, ...]:
    arvot = dict(vektori)
    if vika and vika[0] in arvot:
        arvot[vika[0]] = vika[1]
    for lahto, (a, b) in PORTIT.items():      # topologinen järjestys
        arvot[lahto] = 1 - (arvot[a] & arvot[b])
        if vika and vika[0] == lahto:
            arvot[lahto] = vika[1]
    return tuple(arvot[x] for x in LAHDOT)
# @loppu piiri


# @alku vikasimulointi
def havaitut(vektorit: list[dict[str, int]], viat: list[Vika]
             ) -> set[Vika]:
    tulos = set()
    for v in vektorit:
        oikea = simuloi(v)
        tulos |= {f for f in viat if simuloi(v, f) != oikea}
    return tulos


def tiivista(vektorit: list[dict[str, int]], viat: list[Vika]
             ) -> list[dict[str, int]]:
    """Ahne valinta: otetaan vektori, joka havaitsee eniten jäljellä
    olevia vikoja, kunnes kaikki havaittavat on katettu."""
    jaljella, valitut = set(havaitut(vektorit, viat)), []
    while jaljella:
        paras = max(vektorit, key=lambda v: len(havaitut([v], viat)
                                                 & jaljella))
        valitut.append(paras)
        jaljella -= havaitut([paras], viat)
    return valitut
# @loppu vikasimulointi


def main() -> None:
    johtimet = TULOT + list(PORTIT)
    viat: list[Vika] = [(j, a) for j in johtimet for a in (0, 1)]
    # @alku kattavuus
    rng = random.Random(1)
    satunnaiset = [{t: rng.randint(0, 1) for t in TULOT}
                   for _ in range(16)]
    for n in [1, 2, 4, 8, 16]:
        kate = len(havaitut(satunnaiset[:n], viat)) / len(viat)
        print(f"{n:2} satunnaista vektoria: vikakattavuus {kate:6.1%}")
    kaikki = [dict(zip(TULOT, bitit, strict=True))
              for bitit in product((0, 1), repeat=len(TULOT))]
    testit = tiivista(kaikki, viat)
    print(f"tiivis testijoukko: {len(testit)} vektoria kattaa "
          f"{len(havaitut(testit, viat))}/{len(viat)} vikaa")
    for v in testit:
        print("  " + "".join(str(v[t]) for t in TULOT),
              "->", "".join(map(str, simuloi(v))))
    # @loppu kattavuus


if __name__ == "__main__":
    main()
