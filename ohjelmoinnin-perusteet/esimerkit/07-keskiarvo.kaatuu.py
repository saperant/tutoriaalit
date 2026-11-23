"""Laskee syötteen lukujen keskiarvon. Ei varaudu virheelliseen
syötteeseen."""

import sys


def lue_luvut(rivit: list[str]) -> list[float]:
    luvut = []
    for rivi in rivit:
        luvut.append(float(rivi))
    return luvut


luvut = lue_luvut(sys.stdin.read().splitlines())
print(f"Keskiarvo: {sum(luvut) / len(luvut):.2f}")
