"""Palauttaa litistetyn funktion ohjausvuon tilakoneesta.

Käyttö: python3 litistys.py OHJELMA FUNKTIO

Litistetty funktio on silmukka, jonka välittäjä (dispatcher) vertaa
tilamuuttujaa vakioihin ja hyppää vastaavaan lohkoon. Lohko asettaa
seuraavan tilan ja palaa välittäjään. Skripti

1. tunnistaa tilamuuttujan muistipaikaksi, jota verrataan useimmin
   vakioihin,
2. lukee välittäjän vertailuista taulun tila -> lohkon osoite,
3. kerää kustakin lohkosta tilavakiot, jotka se voi asettaa
   seuraavaksi tilaksi, ja
4. tulostaa tilakoneen leveyshakujärjestyksessä alkutilasta alkaen.
"""

import re
import sys
from collections import Counter, deque
from itertools import pairwise

from purku import Kasky, ilman_tayttoa, pura

VERTAILU = re.compile(r"^(DWORD PTR \[rbp-0x[0-9a-f]+\]),0x([0-9a-f]+)$")
ASETUS = re.compile(r"^(DWORD PTR \[rbp-0x[0-9a-f]+\]|eax),0x([0-9a-f]+)$")


def tilakone(kaskyt: list[Kasky]) -> tuple[str, int, dict[int, int]]:
    """(tilamuuttuja, alkutila, tila -> lohkon alkuosoite)."""
    paikat = Counter(m.group(1) for k in kaskyt if k.nimi == "cmp"
                     and (m := VERTAILU.match(k.operandit)))
    muuttuja = paikat.most_common(1)[0][0]
    taulu = {}
    alkutila = None
    for k, seuraava in pairwise(kaskyt):
        osuma = VERTAILU.match(k.operandit)
        if k.nimi == "cmp" and osuma and osuma.group(1) == muuttuja and \
                seuraava.nimi == "je" and seuraava.kohde is not None:
            taulu[int(osuma.group(2), 16)] = seuraava.kohde
        osuma = ASETUS.match(k.operandit)
        if alkutila is None and k.nimi == "mov" and osuma and \
                osuma.group(1) == muuttuja:
            alkutila = int(osuma.group(2), 16)
    assert alkutila is not None, "alkutilaa ei löytynyt"
    return muuttuja, alkutila, taulu


def lohko(kaskyt: list[Kasky], alku: int, tilat: set[int],
          valittaja: set[int]) -> tuple[int, list[int], bool]:
    """Käy lohkon kaikki polut läpi välittäjään paluuseen asti.

    Palauttaa käskyjen määrän, lohkon asettamat tilat ja tiedon siitä,
    päättyykö jokin polku funktion paluuseen (ret).
    """
    osoitteet = {k.osoite: n for n, k in enumerate(kaskyt)}
    nahdyt: set[int] = set()
    seuraavat: list[int] = []
    paluu = False
    pino = [alku]
    while pino:
        n = osoitteet[pino.pop()]
        while kaskyt[n].osoite not in nahdyt:
            k = kaskyt[n]
            nahdyt.add(k.osoite)
            osuma = ASETUS.match(k.operandit)
            if k.nimi == "mov" and osuma and int(osuma.group(2), 16) in tilat:
                seuraavat.append(int(osuma.group(2), 16))
            if k.nimi == "ret":
                paluu = True
                break
            if k.on_hyppy and k.kohde is not None:
                if k.kohde in valittaja:
                    break
                if k.nimi == "jmp":
                    n = osoitteet[k.kohde]
                    continue
                pino.append(k.kohde)
            n += 1
    return len(nahdyt), seuraavat, paluu


def main() -> None:
    kaskyt = ilman_tayttoa(pura(sys.argv[1])[sys.argv[2]])
    muuttuja, alkutila, taulu = tilakone(kaskyt)
    print(f"tilamuuttuja {muuttuja}, välittäjässä {len(taulu)} tilaa")
    # Välittäjän alku on ensimmäinen tilamuuttujan vertailu; lohkot
    # palaavat sinne suoraan tai yhteisen jmp-käskyn kautta.
    alku = next(k.osoite for k in kaskyt if k.nimi == "cmp"
                and k.operandit.startswith(muuttuja))
    valittaja = {alku} | {k.osoite for k in kaskyt
                          if k.nimi == "jmp" and k.kohde == alku}
    nimet: dict[int, str] = {}
    jono = deque([alkutila])
    while jono:
        tila = jono.popleft()
        if tila in nimet:
            continue
        nimet[tila] = f"T{len(nimet)}"
        _, seuraavat, _ = lohko(kaskyt, taulu[tila], set(taulu), valittaja)
        jono.extend(seuraavat)
    for tila, nimi in nimet.items():
        maara, seuraavat, paluu = lohko(kaskyt, taulu[tila], set(taulu),
                                        valittaja)
        kohteet = [nimet[s] for s in seuraavat] + (["paluu"] if paluu else [])
        kohde = " | ".join(kohteet)
        print(f"{nimi} {tila:#010x} {maara:2} käskyä -> {kohde}")
    for tila in sorted(set(taulu) - set(nimet)):
        print(f"saavuttamaton tila {tila:#010x}")


if __name__ == "__main__":
    main()
