"""Tunnistaa funktioista kääntäjän tuottamia rakenteita.

Käyttö: python3 tunnista.py OHJELMA FUNKTIO...

Tulostaa kustakin funktiosta silmukat (taaksepäin hyppäävät haarat),
hyppytaulut alkioineen, vertailut vakioihin ja muistiviittausten
siirtymät koon mukaan. Osoitteita ei tulosteta, vain suhteelliset
siirtymät, joten tulos ei riipu linkityksestä.
"""

import re
import sys

from purku import Kasky, ilman_tayttoa, lue, pura

MUISTI = re.compile(r"(BYTE|WORD|DWORD|QWORD) PTR \[(\w+)(?:\+(\w+)\*(\d))?"
                    r"(?:\+0x([0-9a-f]+))?\]")
RIP = re.compile(r"\[rip\+0x([0-9a-f]+)\]")


def hyppytaulu(tiedosto: str, kaskyt: list[Kasky], i: int) -> str:
    """Kuvaa epäsuoran hypyn kaskyt[i] taulun, jos sellainen löytyy."""
    raja = taulu = None
    for k in kaskyt[:i]:
        if k.nimi == "cmp" and (osuma := re.search(r",0x([0-9a-f]+)$",
                                                   k.operandit)):
            raja = int(osuma.group(1), 16)
        if k.nimi == "lea" and (osuma := RIP.search(k.operandit)):
            taulu = k.osoite + len(k.tavut) + int(osuma.group(1), 16)
    if raja is None or taulu is None:
        return "epäsuora hyppy, taulua ei löytynyt"
    data = lue(tiedosto, taulu, 4 * (raja + 1))
    alku, loppu = kaskyt[0].osoite, kaskyt[-1].osoite
    kohteet = []
    for n in range(raja + 1):
        siirtyma = int.from_bytes(data[4 * n:4 * n + 4], "little",
                                  signed=True)
        kohde = (taulu + siirtyma) & 0xFFFFFFFFFFFFFFFF
        if not alku <= kohde <= loppu:
            return "epäsuora hyppy, taulun kohde funktion ulkopuolella"
        kohteet.append(kohde)
    return (f"hyppytaulu: {raja + 1} alkiota (arvot 0..{raja}), "
            f"{len(set(kohteet))} eri kohdetta")


def analysoi(tiedosto: str, nimi: str, kaskyt: list[Kasky]) -> None:
    """Tulostaa yhden funktion havainnot."""
    print(f"{nimi}: {len(kaskyt)} käskyä")
    # @alku silmukat
    for i, k in enumerate(kaskyt):
        kohde = k.kohde
        if (k.on_hyppy and k.nimi != "jmp" and kohde is not None
                and kohde <= k.osoite):
            pituus = sum(1 for j in kaskyt if kohde <= j.osoite <= k.osoite)
            print(f"  silmukka: {k.nimi} taaksepäin, "
                  f"runko {pituus} käskyä")
        if k.on_hyppy and kohde is None:
            print("  " + hyppytaulu(tiedosto, kaskyt, i))
    # @loppu silmukat
    vakiot = [k.operandit.split(",")[1] for k in kaskyt
              if k.nimi == "cmp" and ",0x" in k.operandit]
    if vakiot:
        print("  vertailut vakioihin: " +
              ", ".join(str(int(v, 16)) for v in vakiot))
    siirtymat = sorted({(int(m.group(5) or "0", 16), m.group(1))
                        for k in kaskyt
                        for m in MUISTI.finditer(k.operandit)
                        if m.group(2) != "rip" and m.group(3) is None})
    if siirtymat:
        print("  muistiviittaukset: " +
              ", ".join(f"+{s} {koko}" for s, koko in siirtymat))
    askeleet = set()
    for k in kaskyt:
        if osuma := re.match(r"^r\w+,0x([0-9a-f]+)$", k.operandit):
            arvo = int(osuma.group(1), 16)
            if k.nimi == "add":
                askeleet.add(arvo)
            elif k.nimi == "shl":
                askeleet.add(1 << arvo)
    if askeleet:
        print("  osoittimen askel (add, shl): " +
              ", ".join(f"{a} tavua" for a in sorted(askeleet)))


def main() -> None:
    tiedosto, nimet = sys.argv[1], sys.argv[2:]
    funktiot = pura(tiedosto)
    for nimi in nimet:
        analysoi(tiedosto, nimi, ilman_tayttoa(funktiot[nimi]))


if __name__ == "__main__":
    main()
