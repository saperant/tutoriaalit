"""Vertaa samaa ohjelmaa kahdella optimointitasolla.

Käyttö: python3 vertaa.py OHJELMA_O0 OHJELMA_O2 FUNKTIO...

Tulostaa funktioittain käskyjen määrän ja kutsut (call ja häntäkutsuna
käytetty jmp toiseen funktioon) kummastakin käännöksestä.
"""

import sys

from purku import Kasky, ilman_tayttoa, pura


def kutsut(nimi: str, kaskyt: list[Kasky]) -> str:
    """Funktion kutsumat funktiot; häntäkutsu merkitään 'jmp:'."""
    tulos = []
    for k in kaskyt:
        kohde = k.kohdenimi.split("+")[0]
        if k.nimi == "call" and kohde:
            tulos.append(kohde)
        elif k.nimi == "jmp" and kohde and kohde != nimi:
            tulos.append("jmp:" + kohde)
    return " ".join(tulos) or "-"


def main() -> None:
    o0, o2 = pura(sys.argv[1]), pura(sys.argv[2])
    print(f"{'funktio':<10} {'-O0':>4} {'-O2':>4}  kutsut -O0 / -O2")
    for nimi in sys.argv[3:]:
        a, b = ilman_tayttoa(o0[nimi]), ilman_tayttoa(o2[nimi])
        print(f"{nimi:<10} {len(a):>4} {len(b):>4}  "
              f"{kutsut(nimi, a)} / {kutsut(nimi, b)}")


if __name__ == "__main__":
    main()
