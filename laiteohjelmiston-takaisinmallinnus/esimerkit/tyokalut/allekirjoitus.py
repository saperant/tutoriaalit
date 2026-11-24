"""Kirjastofunktioiden tunnistus tavuallekirjoituksista (vrt. IDA:n
FLIRT ja Ghidran Function ID).

Käyttö: python3 allekirjoitus.py tee VIITE.elf KOHDE.json
        python3 allekirjoitus.py etsi KIRJASTO.json KUVA KANTA TAULU LOPPU

Allekirjoitus on funktion alku (enintään 32 tavua), jossa bl-käskyt
on peitetty: niiden kohde riippuu siitä, mihin linkkeri funktiot
sijoitti. Kaikki muu Thumb-koodi on paikkariippumatonta.
"""
import json
import subprocess
import sys

import thumb
from kuva import Kuva

PITUUS = 32


# @alku peita
def peita(koodi: bytes) -> str:
    """Heksajono, jossa 32-bittiset bl-käskyt ovat muodossa '........'."""
    tulos, i = [], 0
    while i + 1 < len(koodi):
        ylempi = koodi[i] | koodi[i + 1] << 8
        if ylempi & 0xF800 == 0xF000 and i + 3 < len(koodi):
            alempi = koodi[i + 2] | koodi[i + 3] << 8
            if alempi & 0xD000 == 0xD000:
                tulos.append("........")
                i += 4
                continue
        tulos.append(koodi[i:i + 2].hex())
        i += 2
    return "".join(tulos)
# @loppu peita


def tee(elf: str, kohde: str) -> None:
    nm = subprocess.run(["arm-none-eabi-nm", "-S", "--defined-only", elf],
                        capture_output=True, text=True, check=True).stdout
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", elf,
                    "viite.bin"], check=True)
    kuva = Kuva.lue("viite.bin", 0)     # viite on linkitetty osoitteeseen 0
    kirjasto = {}
    for rivi in nm.splitlines():
        osat = rivi.split()
        if len(osat) == 4 and osat[2] in "Tt" and osat[3] != "main":
            osoite, koko = int(osat[0], 16), int(osat[1], 16)
            kirjasto[osat[3]] = peita(kuva.tavut(osoite,
                                                 min(koko, PITUUS)))
    with open(kohde, "w") as f:
        json.dump(kirjasto, f, indent=1, sort_keys=True)
    print(f"{len(kirjasto)} allekirjoitusta: {', '.join(sorted(kirjasto))}")


def etsi(kirjasto_polku: str, kuva: Kuva, taulu: int, loppu: int) -> None:
    with open(kirjasto_polku) as f:
        kirjasto: dict[str, str] = json.load(f)
    funktiot = thumb.kaikki_funktiot(kuva, taulu, 32, (taulu, loppu))
    for osoite in sorted(funktiot):
        alku = peita(kuva.tavut(osoite, min(PITUUS, loppu - osoite)))
        for nimi, allekirjoitus in sorted(kirjasto.items()):
            if alku.startswith(allekirjoitus):
                print(f"{osoite:#x}: {nimi}")


def main() -> None:
    if sys.argv[1] == "tee":
        tee(sys.argv[2], sys.argv[3])
    else:
        kuva = Kuva.lue(sys.argv[3], int(sys.argv[4], 0))
        etsi(sys.argv[2], kuva, int(sys.argv[5], 0), int(sys.argv[6], 0))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
