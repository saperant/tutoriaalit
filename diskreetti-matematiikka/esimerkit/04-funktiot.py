"""Injektio, surjektio ja bijektio äärellisillä joukoilla."""

from collections import Counter
from collections.abc import Callable, Iterable


# @alku ominaisuudet
def ominaisuudet(f: Callable[[int], int], maarittely: Iterable[int],
                 maali: set[int]) -> str:
    kuvat = [f(x) for x in maarittely]
    injektio = len(set(kuvat)) == len(kuvat)    # ei kahta samaan
    surjektio = set(kuvat) == maali             # kaikki osuttu
    if injektio and surjektio:
        return "bijektio"
    if injektio:
        return "injektio"
    if surjektio:
        return "surjektio"
    return "ei kumpikaan"


A = range(8)
print("x ↦ 3x mod 8:", ominaisuudet(lambda x: 3 * x % 8, A, set(A)))
print("x ↦ 2x mod 8:", ominaisuudet(lambda x: 2 * x % 8, A, set(A)))
print("x ↦ x // 2  :", ominaisuudet(lambda x: x // 2, A, set(range(4))))
print("x ↦ x + 1   :", ominaisuudet(lambda x: x + 1, A, set(range(9))))
# @loppu ominaisuudet

# @alku hajautus
# Hajautusfunktio avaimilta lokeroihin ei voi olla injektio, jos
# avaimia on enemmän kuin lokeroita: törmäykset ovat väistämättömiä.
avaimet = [f"tuote-{i}" for i in range(20)]
lokeroita = 16


def lokero(avain: str) -> int:
    return sum(avain.encode()) % lokeroita


taytto = Counter(lokero(a) for a in avaimet)
print(f"{len(avaimet)} avainta, {lokeroita} lokeroa,",
      f"suurin lokero {max(taytto.values())} avainta")
# @loppu hajautus

# @alku kaanteis
# Bijektion käänteisfunktio: 3·x mod 8 kumoutuu kertomalla 3:lla,
# koska 3·3 = 9 ≡ 1 (mod 8).
salaa = {x: 3 * x % 8 for x in A}
pura = {y: x for x, y in salaa.items()}
print("pura ∘ salaa = id:", all(pura[salaa[x]] == x for x in A))
print("3·y mod 8 kumoaa:", all(3 * salaa[x] % 8 == x for x in A))
# @loppu kaanteis
