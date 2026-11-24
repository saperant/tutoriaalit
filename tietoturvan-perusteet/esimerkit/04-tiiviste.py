"""Ladatun tiedoston eheyden tarkistus SHA-256-tiivisteellä."""

import hashlib
import tempfile
from pathlib import Path


# @alku tiiviste
def sha256(polku: Path) -> str:
    h = hashlib.sha256()
    with polku.open("rb") as f:
        for lohko in iter(lambda: f.read(65536), b""):
            h.update(lohko)
    return h.hexdigest()
# @loppu tiiviste


with tempfile.TemporaryDirectory() as hak:
    paketti = Path(hak) / "asennus.tar"
    paketti.write_bytes(b"asennuspaketin sisalto v1.4.2\n" * 1000)
    # Julkaisija ilmoittaa tiivisteen eri kanavaa pitkin (esim. HTTPS-
    # sivulla tai allekirjoitettuna), muuten se ei suojaa mitään.
    julkaistu = sha256(paketti)

    print("alkuperäinen:", sha256(paketti) == julkaistu)
    data = bytearray(paketti.read_bytes())
    data[5000] ^= 0x01                      # yksi bitti muuttuu
    paketti.write_bytes(bytes(data))
    print("yksi bitti muutettu:", sha256(paketti) == julkaistu)
