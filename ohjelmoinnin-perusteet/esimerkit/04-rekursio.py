"""Kertoma kahdella tavalla: rekursiolla ja silmukalla."""


def kertoma(n: int) -> int:
    """Palauttaa luvun n kertoman n! = n * (n - 1) * ... * 1."""
    if n <= 1:                      # päättymisehto: ei uutta kutsua
        return 1
    return n * kertoma(n - 1)       # sama tehtävä pienemmällä luvulla


def kertoma_silmukalla(n: int) -> int:
    """Sama tulos ilman rekursiota."""
    tulos = 1
    for kerroin in range(2, n + 1):
        tulos = tulos * kerroin
    return tulos


for n in [1, 4, 10]:
    print(f"{n}! = {kertoma(n)} = {kertoma_silmukalla(n)}")
