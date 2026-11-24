"""Puiden ominaisuudet: n - 1 kaarta, ei syklejä ja Cayleyn kaava."""

from itertools import combinations

Kaari = tuple[int, int]


# @alku puu
def on_puu(n: int, kaaret: list[Kaari]) -> bool:
    """Puu = yhtenäinen ja syklitön. Union–find tunnistaa syklin."""
    vanhempi = list(range(n))

    def juuri(x: int) -> int:
        while vanhempi[x] != x:
            vanhempi[x] = vanhempi[vanhempi[x]]   # polun puolitus
            x = vanhempi[x]
        return x

    for a, b in kaaret:
        ra, rb = juuri(a), juuri(b)
        if ra == rb:
            return False                          # kaari sulkisi syklin
        vanhempi[ra] = rb
    return len(kaaret) == n - 1                   # yhtenäinen
# @loppu puu


# @alku cayley
# Cayleyn kaava: n numeroidulla solmulla on n^(n-2) erilaista puuta.
# Tarkistus kokeilemalla kaikki (n - 1)-kaariset kaarijoukot.
for n in range(2, 7):
    kaikki_kaaret = list(combinations(range(n), 2))
    puita = sum(1 for k in combinations(kaikki_kaaret, n - 1)
                if on_puu(n, list(k)))
    print(f"n = {n}: {puita:>4} puuta, n^(n-2) = {n**(n - 2):>4}")
# @loppu cayley

# @alku ominaisuudet
# Kaaren lisääminen puuhun synnyttää syklin, poistaminen katkaisee sen.
puu = [(0, 1), (1, 2), (1, 3), (3, 4)]
print("puu:", on_puu(5, puu))
print("+ kaari (2, 4):", on_puu(5, [*puu, (2, 4)]))
print("- kaari (1, 3):", on_puu(5, [k for k in puu if k != (1, 3)]))
# @loppu ominaisuudet
