"""Purkaa ohjelman XOR-salatut merkkijonot staattisesti.

Käyttö: python3 pura_xor.py OHJELMA PURKUFUNKTIO

1. Avaimen parametrit luetaan purkufunktion koodista: rekisteri, joka
   alustetaan vakiolla (mov), XORataan dataan (xor) ja jota kasvatetaan
   vakiolla (add), on avain: k[i] = alku + i * askel.
2. .rodata-osio käydään läpi. Kohta on salatun jonon alku, jos
   purettuna siitä alkaa vähintään kuuden tulostuvan merkin jono, joka
   päättyy nollatavuun.
"""

import re
import sys

from purku import ilman_tayttoa, lue, osiot, pura

MOV = re.compile(r"^(\w+),0x([0-9a-f]+)$")


def avain(ohjelma: str, funktio: str) -> tuple[int, int]:
    """(alku, askel) purkufunktion käskyistä."""
    kaskyt = ilman_tayttoa(pura(ohjelma)[funktio])
    alut = {m.group(1): int(m.group(2), 16) for k in kaskyt
            if k.nimi == "mov" and (m := MOV.match(k.operandit))}
    for k in kaskyt:
        if k.nimi == "add" and (m := MOV.match(k.operandit)):
            rekisteri = m.group(1)
            if rekisteri in alut and any(
                    x.nimi == "xor" and x.operandit.endswith("," + rekisteri)
                    for x in kaskyt):
                return alut[rekisteri], int(m.group(2), 16)
    raise ValueError("avainta ei löytynyt")


def rodata(ohjelma: str) -> bytes:
    """.rodata-osion sisältö."""
    for nimi, osoite, _, koko in osiot(ohjelma):
        if nimi == ".rodata":
            return lue(ohjelma, osoite, koko)
    raise ValueError(".rodata puuttuu")


def main() -> None:
    ohjelma, funktio = sys.argv[1], sys.argv[2]
    alku, askel = avain(ohjelma, funktio)
    print(f"avain purkufunktiosta: alku {alku:#04x}, askel {askel:#04x}")
    data = rodata(ohjelma)
    kohta = 0
    while kohta < len(data):
        selko = bytearray()
        for i in range(len(data) - kohta):
            merkki = data[kohta + i] ^ ((alku + i * askel) & 0xFF)
            if merkki == 0 or not 32 <= merkki < 127:
                break
            selko.append(merkki)
        loppu = kohta + len(selko)
        if len(selko) >= 6 and loppu < len(data) and \
                data[loppu] ^ ((alku + len(selko) * askel) & 0xFF) == 0:
            print(f".rodata+{kohta:#05x}: {selko.decode()}")
            kohta = loppu + 1
        else:
            kohta += 1


if __name__ == "__main__":
    main()
