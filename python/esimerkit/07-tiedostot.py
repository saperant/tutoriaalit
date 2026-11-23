"""Tiedostojen käsittely pathlibillä ja atominen tallennus."""

import json
import os
import tempfile
from pathlib import Path


# @alku atominen
def tallenna_atomisesti(polku: Path, sisalto: str) -> None:
    """Kirjoittaa väliaikaiseen tiedostoon ja vaihtaa sen paikalleen.

    Lukija näkee aina joko vanhan tai uuden version, ei koskaan puoliksi
    kirjoitettua tiedostoa, vaikka ohjelma kaatuisi kesken.
    """
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=polku.parent, delete=False
    ) as tmp:
        tmp.write(sisalto)
        tmp.flush()
        os.fsync(tmp.fileno())
    os.replace(tmp.name, polku)
# @loppu atominen


# @alku kaytto
hakemisto = Path("asetukset")
hakemisto.mkdir(exist_ok=True)
polku = hakemisto / "palvelu.json"

tallenna_atomisesti(polku, json.dumps({"portti": 8080, "debug": False}))
asetukset = json.loads(polku.read_text(encoding="utf-8"))
print(asetukset["portti"], polku.suffix, polku.stem)

for tiedosto in sorted(Path(".").rglob("*.json")):
    print(tiedosto, tiedosto.stat().st_size, "tavua")
# @loppu kaytto
