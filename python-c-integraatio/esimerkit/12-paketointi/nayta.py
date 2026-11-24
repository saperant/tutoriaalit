"""Tulostaa pyöräpaketin nimen ja paketin tiedostot ilman
Python-versiosta riippuvia osia (esim. cp312 → cpXY)."""

import re
import sys
import zipfile
from pathlib import Path


def yleista(nimi: str) -> str:
    nimi = re.sub(r"cp3\d+", "cpXY", nimi)
    return re.sub(r"cpython-3\d+", "cpython-3XY", nimi)


def main() -> None:
    pyora = next(Path(sys.argv[1]).glob("*.whl"))
    print("pyörä:", yleista(pyora.name))
    with zipfile.ZipFile(pyora) as z:
        for nimi in sorted(z.namelist()):
            if not nimi.startswith("nopeatarkiste-"):   # ei metatietoja
                print("  ", yleista(nimi))


if __name__ == "__main__":
    main()
