"""TOCTOU: tarkistuksen ja käytön välissä tilanne ehtii muuttua."""

import os
import tempfile
from collections.abc import Callable
from pathlib import Path


# @alku haavoittuva
def kirjoita_haavoittuva(polku: Path, teksti: str,
                         valissa: Callable[[], None]) -> None:
    if polku.exists():                       # tarkistus (check)
        raise FileExistsError(polku)
    valissa()                                # kilpailutilanteen ikkuna
    polku.write_text(teksti)                 # käyttö (use)
# @loppu haavoittuva


# @alku korjattu
def kirjoita(polku: Path, teksti: str,
             valissa: Callable[[], None]) -> None:
    valissa()
    # Tarkistus ja luonti ovat yksi atominen järjestelmäkutsu: O_EXCL
    # epäonnistuu, jos nimi on jo olemassa, myös symbolisena linkkinä.
    fd = os.open(polku, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                 | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(teksti)
# @loppu korjattu


with tempfile.TemporaryDirectory() as hak:
    jaettu = Path(hak)                       # kuten /tmp
    arvokas = jaettu / "asetukset.conf"
    arvokas.write_text("tärkeät asetukset\n")
    raportti = jaettu / "raportti.txt"

    def hyokkaaja() -> None:                 # ehtii väliin
        raportti.symlink_to(arvokas)

    kirjoita_haavoittuva(raportti, "raportin sisältö\n", hyokkaaja)
    print("haavoittuva, asetukset nyt:", arvokas.read_text(), end="")

    raportti.unlink()
    arvokas.write_text("tärkeät asetukset\n")
    try:
        kirjoita(raportti, "raportin sisältö\n", hyokkaaja)
    except FileExistsError:
        print("korjattu: kirjoitus estetty")
    print("korjattu, asetukset nyt:", arvokas.read_text(), end="")
