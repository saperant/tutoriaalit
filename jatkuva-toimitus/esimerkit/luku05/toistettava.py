"""Sama lähdekoodi, kaksi rakennusta: tuleeko sama artefakti?

Lähdepuu kopioidaan kahteen hakemistoon eri aikaleimoin, kuten kävisi
kahdella rakennuskoneella. Naiivi paketti eroaa, toistettava ei.
"""

import os
import shutil
import tempfile
from pathlib import Path

from toimitus.artefakti import (
    lahdetiiviste,
    lahdetiedostot,
    rakenna,
    rakenna_naiivisti,
    tiiviste,
)

SOVELLUS = Path(__file__).resolve().parent.parent / "sovellus"


def kopio(kohde: Path, aikaleima: int) -> Path:
    shutil.copytree(SOVELLUS, kohde,
                    ignore=shutil.ignore_patterns("__pycache__"))
    for polku in lahdetiedostot(kohde):
        os.utime(polku, (aikaleima, aikaleima))
    return kohde


with tempfile.TemporaryDirectory() as tmp:
    kone_a = kopio(Path(tmp) / "a" / "sovellus", 1_770_000_000)
    kone_b = kopio(Path(tmp) / "b" / "sovellus", 1_770_086_400)
    # @alku vertailu
    versio = f"1.4.0+{lahdetiiviste(kone_a)[:8]}"
    sama_lahde = lahdetiiviste(kone_a) == lahdetiiviste(kone_b)
    naiivi = [tiiviste(rakenna_naiivisti(kone, kone / "dist", versio))
              for kone in (kone_a, kone_b)]
    toistettava = [tiiviste(rakenna(kone, kone / "dist", versio))
                   for kone in (kone_a, kone_b)]
    # @loppu vertailu
    print(f"lähdepuut samat: {'kyllä' if sama_lahde else 'ei'}")
    print(f"naiivi paketti sama: "
          f"{'kyllä' if naiivi[0] == naiivi[1] else 'ei'}")
    print(f"toistettava paketti sama: "
          f"{'kyllä' if toistettava[0] == toistettava[1] else 'ei'}")
    print(f"version muoto: 1.4.0+<{len(versio.split('+')[1])} merkkiä "
          "lähdepuun tiivisteestä>")
