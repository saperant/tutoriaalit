"""Rakenna kerran, vie sama artefakti testiin ja tuotantoon.

Ympäristöt ovat hakemistoja. Sama paketti puretaan kumpaankin, ja erot
tulevat vain ympäristömuuttujista. Lopuksi viallinen julkaisu perutaan.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from toimitus.artefakti import lahdetiiviste, ota_kayttoon, peru, rakenna

SOVELLUS = Path(__file__).resolve().parent.parent / "sovellus"


def aja(ymparisto: Path, nimi: str, *argumentit: str,
        ryhmittely: str = "1") -> str:
    """Ajaa ympäristön nykyisen version sen omilla asetuksilla."""
    muuttujat = {**os.environ, "VIITE_YMPARISTO": nimi,
                 "VIITE_RYHMITTELY": ryhmittely}
    tulos = subprocess.run(
        [sys.executable, "-B", "-m", "viite", *argumentit],
        cwd=ymparisto / "nykyinen", env=muuttujat,
        capture_output=True, text=True, check=True)
    return tulos.stdout.strip()


with tempfile.TemporaryDirectory() as tmp:
    juuri = Path(tmp)
    testi, tuotanto = juuri / "testi", juuri / "tuotanto"
    # @alku edistaminen
    versio = f"1.4.0+{lahdetiiviste(SOVELLUS)[:8]}"
    artefakti = rakenna(SOVELLUS, juuri / "varasto", versio)   # kerran
    testissa = ota_kayttoon(artefakti, testi)
    assert aja(testi, "testi", "tarkista", "1234561") == "kelpaa"
    tuotannossa = ota_kayttoon(artefakti, tuotanto)            # sama tiedosto
    # @loppu edistaminen
    print(f"sama artefakti: {'kyllä' if testissa == tuotannossa else 'ei'}")
    for ymparisto, nimi, ryhmittely in ((testi, "testi", "1"),
                                        (tuotanto, "tuotanto", "0")):
        rivi = aja(ymparisto, nimi, "versio").replace(versio, "<versio>")
        viite = aja(ymparisto, nimi, "muodosta", "123456",
                    ryhmittely=ryhmittely)
        print(f"{nimi:<9}{rivi:<30}{viite}")

    # Seuraava versio osoittautuu vialliseksi tuotannossa: perutaan.
    uusi = rakenna(SOVELLUS, juuri / "varasto", "1.5.0+viallinen")
    ota_kayttoon(uusi, tuotanto)
    print("uusi käytössä:", aja(tuotanto, "tuotanto", "versio"))
    peru(tuotanto)
    palattu = aja(tuotanto, "tuotanto", "versio").replace(versio, "<versio>")
    print("perumisen jälkeen:", palattu)
