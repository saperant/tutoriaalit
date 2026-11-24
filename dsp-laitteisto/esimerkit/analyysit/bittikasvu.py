"""Esimerkin FIR-suotimen bittileveydet: tulo, summa ja ulostulo
pahimman tapauksen mukaan.

Käyttö: python3 analyysit/bittikasvu.py
"""

from __future__ import annotations

import math

from malli.kertoimet import DATA_BITIT, FIR, KERROIN_BITIT, KERROIN_MURTO
from malli.kiintea import alue, leveys, pyorista


# @alku kasvu
def summan_alue(h: list[int], bitit: int) -> tuple[int, int]:
    """Summan sum h[k] x[n-k] pienin ja suurin mahdollinen arvo, kun
    jokainen x on alueella [-2**(b-1), 2**(b-1) - 1]."""
    pienin, suurin = alue(bitit)
    ala = sum(c * (suurin if c < 0 else pienin) for c in h)
    yla = sum(c * (suurin if c > 0 else pienin) for c in h)
    return ala, yla


def main() -> None:
    n = len(FIR)
    tulo = DATA_BITIT + KERROIN_BITIT
    yleinen = tulo + math.ceil(math.log2(n))
    ala, yla = summan_alue(FIR, DATA_BITIT)
    tarkka = leveys(ala, yla)
    print(f"tulo: {DATA_BITIT} + {KERROIN_BITIT} = {tulo} bittiä")
    print(
        f"summa, mitkä tahansa {n} kerrointa: {tulo} + "
        f"log2({n}) = {yleinen} bittiä"
    )
    print(f"summa näillä kertoimilla: [{ala}, {yla}] -> {tarkka} bittiä")
    lyhyt = (pyorista(ala, KERROIN_MURTO), pyorista(yla, KERROIN_MURTO))
    print(
        f"pyöristetty ulostulo: [{lyhyt[0]}, {lyhyt[1]}] -> "
        f"{leveys(*lyhyt)} bittiä, sallittu {alue(DATA_BITIT)}"
    )
    l1 = sum(abs(c) for c in FIR) / (1 << KERROIN_MURTO)
    print(f"kertoimien itseisarvojen summa {l1:.4f} = suurin vahvistus")
    # @loppu kasvu


if __name__ == "__main__":
    main()
