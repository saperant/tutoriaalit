"""Quine–McCluskeyn menetelmä: pienin tulojen summa totuustaulusta.

Termi esitetään merkkijonona, jossa jokainen merkki on yksi muuttuja:
'1' (muuttuja), '0' (komplementti) tai '-' (muuttuja ei esiinny).
Esimerkiksi neljän muuttujan termi '1-0-' tarkoittaa ac'.

Muut esimerkit tuovat tämän modulin (`from qm import sievenna`).
Suoraan ajettuna se sieventää alkulukufunktion.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations


# @alku yhdista
def yhdista(a: str, b: str) -> str | None:
    """Yhdistää termit, jotka eroavat täsmälleen yhdessä bitissä:
    xy + xy' = x."""
    erot = [i for i, (p, q) in enumerate(zip(a, b, strict=True)) if p != q]
    if len(erot) != 1 or "-" in (a[erot[0]], b[erot[0]]):
        return None
    i = erot[0]
    return a[:i] + "-" + a[i + 1:]
# @loppu yhdista


# @alku alkutermit
def alkutermit(termit: set[str]) -> set[str]:
    """Yhdistää termejä niin kauan kuin voi. Termit, joita ei voi
    yhdistää mihinkään, ovat alkutermejä (prime implicants)."""
    alku: set[str] = set()
    while termit:
        kaytetyt: set[str] = set()
        uudet: set[str] = set()
        for a, b in combinations(sorted(termit), 2):
            c = yhdista(a, b)
            if c is not None:
                uudet.add(c)
                kaytetyt |= {a, b}
        alku |= termit - kaytetyt
        termit = uudet
    return alku
# @loppu alkutermit


def kattaa(termi: str, minterm: int) -> bool:
    bitit = format(minterm, f"0{len(termi)}b")
    return all(t in ("-", b) for t, b in zip(termi, bitit, strict=True))


# @alku peitto
def sievenna(n: int, ykkoset: list[int],
             yhdentekevat: list[int] | None = None) -> list[str]:
    """Palauttaa pienen joukon alkutermejä, jotka kattavat ykköset.
    Yhdentekevät (don't care) rivit saavat auttaa yhdistämisessä,
    mutta niitä ei tarvitse kattaa."""
    kaikki = set(ykkoset) | set(yhdentekevat or [])
    alku = alkutermit({format(m, f"0{n}b") for m in kaikki})
    kattamatta = set(ykkoset)
    valitut: list[str] = []
    # Välttämättömät alkutermit: ainoa termi, joka kattaa jonkin ykkösen.
    for m in sorted(ykkoset):
        kattajat = [t for t in alku if kattaa(t, m)]
        if len(kattajat) == 1 and kattajat[0] not in valitut:
            valitut.append(kattajat[0])
    for t in valitut:
        kattamatta -= {m for m in ykkoset if kattaa(t, m)}
    # Loput ahneesti: termi, joka kattaa eniten jäljellä olevia.
    while kattamatta:
        paras = max(sorted(alku), key=lambda t: sum(
            kattaa(t, m) for m in kattamatta))
        valitut.append(paras)
        kattamatta -= {m for m in kattamatta if kattaa(paras, m)}
    return sorted(valitut)
# @loppu peitto


def lauseke(termit: list[str], nimet: Sequence[str] = "abcd") -> str:
    """Termit luettavana lausekkeena; monimerkkiset nimet erotetaan
    pisteellä (q1·q0')."""
    erotin = "" if all(len(n) == 1 for n in nimet) else "·"
    osat = []
    for t in termit:
        osat.append(erotin.join(nimet[i] + ("" if b == "1" else "'")
                                for i, b in enumerate(t) if b != "-") or "1")
    return " + ".join(osat) or "0"


if __name__ == "__main__":
    # @alku alkuluku
    alkuluvut = [2, 3, 5, 7, 11, 13]
    t = sievenna(4, alkuluvut)
    print(f"alkuluku(abcd), 0–15:   {lauseke(t)}")
    # BCD-koodissa koodit 10–15 eivät esiinny: ne ovat yhdentekeviä.
    t = sievenna(4, [2, 3, 5, 7], yhdentekevat=list(range(10, 16)))
    print(f"alkuluku(abcd), BCD:    {lauseke(t)}")
    # @loppu alkuluku
