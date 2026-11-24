"""Päättelyjen tarkistus symbolitaulusta (kun ELF on saatavilla).

Käyttö: python3 vastaus.py ELF KUVA KANTA TAULU LOPPU [OSOITE=NIMI...]

Vertaa löydettyjä funktioiden alkuja ELF-tiedoston funktiosymboleihin
ja tarkistaa annetut nimeämiset. Oikeassa työssä ELF:ää ei ole; tässä
se on oppimateriaalin vastausavain.
"""
import subprocess
import sys

import thumb
from kuva import Kuva


def symbolit(elf: str) -> dict[int, str]:
    """Funktiosymbolit (tyyppi FUNC) ilman Thumb-bittiä."""
    readelf = subprocess.run(["arm-none-eabi-readelf", "-sW", elf],
                             capture_output=True, text=True,
                             check=True).stdout
    tulos = {}
    for rivi in readelf.splitlines():
        osat = rivi.split()
        if len(osat) == 8 and osat[3] == "FUNC":
            tulos[int(osat[1], 16) & ~1] = osat[7]
    return tulos


def main() -> None:
    nimet = symbolit(sys.argv[1])
    kuva = Kuva.lue(sys.argv[2], int(sys.argv[3], 0))
    taulu, loppu = int(sys.argv[4], 0), int(sys.argv[5], 0)
    funktiot = thumb.kaikki_funktiot(kuva, taulu, 32, (taulu, loppu))
    koodia = set(nimet)
    oikein = koodia & funktiot.keys()
    print(f"ELF:n funktioita {len(koodia)}, löydettiin {len(funktiot)}, "
          f"oikein {len(oikein)}")
    for osoite in sorted(koodia - funktiot.keys()):
        print(f"  löytymättä: {osoite:#x} {nimet[osoite]}")
    for osoite in sorted(funktiot.keys() - koodia):
        print(f"  väärä löytö: {osoite:#x}")
    for pari in sys.argv[6:]:
        osoite_teksti, arvaus = pari.split("=")
        osoite = int(osoite_teksti, 0)
        todellinen = nimet.get(osoite, "?")
        tulos = "oikein" if todellinen == arvaus else "VÄÄRIN"
        print(f"  {osoite:#x} {arvaus}: {tulos} ({todellinen})")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
