"""Rakenteiden hintaeroja: vain suuruusluokat, ei tarkkoja aikoja."""

import timeit
from collections import deque

N = 50_000


# @alku hinnat
def tyhjenna_lista() -> None:
    jono = list(range(N))
    while jono:
        jono.pop(0)               # O(n): siirtää kaikki alkiot


def tyhjenna_deque() -> None:
    jono = deque(range(N))
    while jono:
        jono.popleft()            # O(1)


lista = list(range(N))
joukko = set(lista)
haut = range(N - 100, N)


def hae_listasta() -> int:
    return sum(1 for x in haut if x in lista)       # O(n) per haku


def hae_joukosta() -> int:
    return sum(1 for x in haut if x in joukko)      # O(1) per haku


for hidas, nopea in [(tyhjenna_lista, tyhjenna_deque),
                     (hae_listasta, hae_joukosta)]:
    suhde = (timeit.timeit(hidas, number=1)
             / timeit.timeit(nopea, number=1))
    print(f"{nopea.__name__} yli 10 kertaa nopeampi: {suhde > 10}")
# @loppu hinnat
