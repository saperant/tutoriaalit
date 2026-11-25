"""Toimitusputki esimerkkisovellukselle: ehjä ja rikkinäinen muutos.

Putki ajetaan sovelluksen kopiolle väliaikaisessa hakemistossa, kuten
CI-palvelin ajaa sen puhtaalle työkopiolle.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from toimitus.artefakti import lahdetiiviste, rakenna
from toimitus.putki import Toiminto, Vaihe, aja, tulosta

SOVELLUS = Path(__file__).resolve().parent.parent / "sovellus"


def komento(*argumentit: str) -> Toiminto:
    """Vaihe, joka onnistuu, jos komento palauttaa nollan."""
    def toiminto(tyohak: Path) -> bool:
        ymparisto = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        tulos = subprocess.run(argumentit, cwd=tyohak, env=ymparisto,
                               capture_output=True, check=False)
        return tulos.returncode == 0
    return toiminto


def paketoi(tyohak: Path) -> bool:
    versio = f"1.4.0+{lahdetiiviste(tyohak)[:8]}"
    rakenna(tyohak, tyohak / "dist", versio)
    return True


def savutesti(tyohak: Path) -> bool:
    """Purkaa valmiin paketin ja ajaa sen: testataan se, mikä toimitetaan."""
    paketti = next((tyohak / "dist").glob("viite-*.tar.gz"))
    with tempfile.TemporaryDirectory() as tmp:
        shutil.unpack_archive(paketti, tmp, filter="data")
        tulos = subprocess.run(
            [sys.executable, "-B", "-m", "viite", "tarkista", "1234561"],
            cwd=tmp, capture_output=True, text=True, check=False)
    return tulos.stdout.strip() == "kelpaa"


# @alku vaiheet
PYTHON = sys.executable
PUTKI = [
    Vaihe("tyyli", komento("ruff", "check", "--no-cache", "--quiet", ".")),
    Vaihe("tyypit", komento("mypy", "--cache-dir", os.devnull, "viite")),
    Vaihe("testit", komento(PYTHON, "-m", "pytest", "testit")),
    Vaihe("paketti", paketoi, tarvitsee=("tyyli", "tyypit", "testit")),
    Vaihe("savutesti", savutesti, tarvitsee=("paketti",)),
]
# @loppu vaiheet


def aja_muutos(otsikko: str, vanha: str = "", uusi: str = "") -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tyohak = Path(tmp) / "sovellus"
        shutil.copytree(SOVELLUS, tyohak,
                        ignore=shutil.ignore_patterns("__pycache__"))
        if vanha:
            lahde = tyohak / "viite" / "laskenta.py"
            lahde.write_text(lahde.read_text("utf-8").replace(vanha, uusi),
                             "utf-8")
        print(otsikko)
        tulosta(aja(PUTKI, tyohak))


aja_muutos("ehjä muutos")
aja_muutos("rikkinäinen muutos: kertoimet (7, 3, 2)",
           "KERTOIMET = (7, 3, 1)", "KERTOIMET = (7, 3, 2)")
