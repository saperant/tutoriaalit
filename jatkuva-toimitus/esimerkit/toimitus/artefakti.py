"""Artefaktin rakennus, tunnistus ja käyttöönotto hakemistoihin.

Artefakti rakennetaan kerran ja sama tiedosto viedään ympäristöstä
toiseen. Jotta sama lähdekoodi tuottaisi aina saman tiedoston, paketista
poistetaan kaikki, mikä riippuu rakennushetkestä tai -koneesta.
"""

import gzip
import hashlib
import io
import tarfile
from pathlib import Path

OHITA = {"__pycache__", "testit", "dist", ".pytest_cache", ".mypy_cache"}


def lahdetiedostot(lahde: Path) -> list[Path]:
    """Paketoitavat tiedostot aakkosjärjestyksessä."""
    return sorted(p for p in lahde.rglob("*")
                  if p.is_file() and not OHITA & set(p.parts))


def lahdetiiviste(lahde: Path) -> str:
    """Tiiviste lähdepuun sisällöstä: sama sisältö, sama tunniste."""
    summa = hashlib.sha256()
    for polku in lahdetiedostot(lahde):
        summa.update(str(polku.relative_to(lahde)).encode("utf-8") + b"\0")
        summa.update(polku.read_bytes() + b"\0")
    return summa.hexdigest()


def tiiviste(tiedosto: Path) -> str:
    return hashlib.sha256(tiedosto.read_bytes()).hexdigest()


# @alku toistettava
def rakenna(lahde: Path, kohde: Path, versio: str) -> Path:
    """Rakentaa toistettavan paketin: aika, omistaja ja järjestys vakiot."""
    puskuri = io.BytesIO()
    with tarfile.open(fileobj=puskuri, mode="w") as paketti:
        def lisaa(nimi: str, sisalto: bytes) -> None:
            tieto = tarfile.TarInfo(nimi)
            tieto.size = len(sisalto)
            tieto.mtime = 0                     # ei rakennushetkeä
            tieto.mode = 0o644
            tieto.uid = tieto.gid = 0           # ei rakentajan tunnusta
            tieto.uname = tieto.gname = ""
            paketti.addfile(tieto, io.BytesIO(sisalto))

        for polku in lahdetiedostot(lahde):     # aina sama järjestys
            lisaa(str(polku.relative_to(lahde)), polku.read_bytes())
        lisaa("viite/VERSIO", (versio + "\n").encode("utf-8"))
    kohde.mkdir(parents=True, exist_ok=True)
    tiedosto = kohde / f"viite-{versio}.tar.gz"
    with gzip.GzipFile(tiedosto, "wb", mtime=0) as pakattu:
        pakattu.write(puskuri.getvalue())
    return tiedosto
# @loppu toistettava


def rakenna_naiivisti(lahde: Path, kohde: Path, versio: str) -> Path:
    """Tavallinen tar: mukaan tulevat tiedostojen ajat ja pakkaushetki."""
    kohde.mkdir(parents=True, exist_ok=True)
    tiedosto = kohde / f"viite-{versio}-naiivi.tar.gz"
    with tarfile.open(tiedosto, "w:gz") as paketti:
        for polku in lahdetiedostot(lahde):
            paketti.add(polku, str(polku.relative_to(lahde)))
    return tiedosto


# @alku kayttoonotto
def ota_kayttoon(artefakti: Path, ymparisto: Path) -> str:
    """Purkaa artefaktin omaan hakemistoonsa ja vaihtaa linkin siihen."""
    tunniste = tiiviste(artefakti)[:12]
    kohde = ymparisto / "julkaisut" / tunniste
    if not kohde.exists():
        with tarfile.open(artefakti) as paketti:
            paketti.extractall(kohde, filter="data")
    nykyinen = ymparisto / "nykyinen"
    if nykyinen.is_symlink():
        edellinen = ymparisto / "edellinen"
        edellinen.unlink(missing_ok=True)
        edellinen.symlink_to(nykyinen.readlink())
    valiaikainen = ymparisto / "nykyinen.uusi"
    valiaikainen.unlink(missing_ok=True)
    valiaikainen.symlink_to(kohde)
    valiaikainen.replace(nykyinen)       # vaihto on yksi atominen askel
    return tunniste


def peru(ymparisto: Path) -> None:
    """Palaa edelliseen julkaisuun: vanha versio on yhä levyllä."""
    edellinen = ymparisto / "edellinen"
    valiaikainen = ymparisto / "nykyinen.uusi"
    valiaikainen.unlink(missing_ok=True)
    valiaikainen.symlink_to(edellinen.readlink())
    valiaikainen.replace(ymparisto / "nykyinen")
# @loppu kayttoonotto
