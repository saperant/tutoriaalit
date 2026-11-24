"""Atominen kirjoitus: lukija näkee joko vanhan tai uuden tiedoston,
ei koskaan puolikasta, vaikka kirjoittaja kaatuisi kesken."""

import json
import os
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO


# @alku atominen
@contextmanager
def atominen_kirjoitus(kohde: Path) -> Iterator[TextIO]:
    """Kirjoittaa ensin samaan hakemistoon tilapäistiedostoon ja vaihtaa
    sen kohteen tilalle vasta onnistuneen kirjoituksen jälkeen.

    os.replace on POSIX-järjestelmissä atominen saman tiedosto-
    järjestelmän sisällä, siksi tilapäistiedosto on kohteen vieressä.
    """
    fd, tilapainen = tempfile.mkstemp(dir=kohde.parent,
                                      prefix=f".{kohde.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yield f
            f.flush()
            os.fsync(f.fileno())     # data levylle ennen nimen vaihtoa
        os.replace(tilapainen, kohde)
    except BaseException:
        os.unlink(tilapainen)
        raise
# @loppu atominen


# @alku kaytto
def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        kohde = Path(tmp) / "tulokset.json"
        with atominen_kirjoitus(kohde) as f:
            json.dump({"läpi": 41, "epäonnistui": 1}, f,
                      ensure_ascii=False)
        print("1:", kohde.read_text(encoding="utf-8"))

        try:
            with atominen_kirjoitus(kohde) as f:
                f.write('{"läpi": 4')        # kesken jäävä kirjoitus
                raise KeyboardInterrupt      # esim. Ctrl+C
        except KeyboardInterrupt:
            print("keskeytetty")
        print("2:", kohde.read_text(encoding="utf-8"))
        print("jäljelle jäi:", sorted(p.name for p in Path(tmp).iterdir()))
    return 0
# @loppu kaytto


if __name__ == "__main__":
    sys.exit(main())
