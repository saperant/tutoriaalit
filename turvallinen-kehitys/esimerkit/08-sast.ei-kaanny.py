"""Staattinen analyysi löytää vaarallisen kutsun ennen katselmointia.

Ruffin sääntö S202 (flake8-bandit) varoittaa tar-arkiston purusta
ilman suodatinta: arkiston polku "../" voi kirjoittaa minne tahansa.
Rivi, jolla on merkintä @virhe, kaataa CI:n tarkistuksen; korjattu
versio käyttää Pythonin purkusuodatinta (PEP 706).
"""

import io
import tarfile
from pathlib import Path


# @alku pura
def pura(arkisto: Path, kohde: Path) -> None:
    with tarfile.open(arkisto) as tar:
        tar.extractall(kohde)  # @virhe
        tar.extractall(kohde, filter="data")
# @loppu pura


def tee_arkisto(polku: Path, nimi: str) -> None:
    with tarfile.open(polku, "w") as tar:
        data = b"ladattu sisalto\n"
        tieto = tarfile.TarInfo(nimi)
        tieto.size = len(data)
        tar.addfile(tieto, io.BytesIO(data))


def main() -> None:
    kohde = Path("purku")
    kohde.mkdir()
    for nimi in ("raportti.txt", "../../home/kayttaja/.bashrc"):
        arkisto = Path("paketti.tar")
        tee_arkisto(arkisto, nimi)
        try:
            pura(arkisto, kohde)
            print(f"purettu: {nimi}")
        except tarfile.FilterError as virhe:
            print(f"hylätty: {nimi} ({type(virhe).__name__})")


if __name__ == "__main__":
    main()
