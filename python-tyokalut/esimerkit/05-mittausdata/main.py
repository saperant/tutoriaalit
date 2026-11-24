"""Kirjoittaa MDAT-tiedoston, lukee sen takaisin ja kokeilee, että
rikkinäiset tiedostot hylätään."""

import sys
import tempfile
from pathlib import Path

from muoto import MuotoVirhe, kirjoita, lue


# @alku kaytto
def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        polku = Path(tmp) / "mittaus.mdat"
        jannite = [0, 1200, 2400, 1200, 0, -1200, -2400, -1200]
        virta = [10, 12, 15, 12, 10, 8, 5, 8]
        kirjoita(polku, 48_000, [jannite, virta])
        m = lue(polku)
        print(f"{polku.stat().st_size} tavua, {m.kanavia} kanavaa, "
              f"{m.naytteita} näytettä, {m.taajuus} Hz")
        print("kanava 0:", m.kanava(0))
        print("kanava 1:", m.kanava(1))

        raaka = bytearray(polku.read_bytes())
        for kuvaus, rikottu in (
                ("tavu muuttunut", raaka[:20] + b"\x00" + raaka[21:]),
                ("katkennut", raaka[:30]),
                ("väärä tiedosto", b"PK\x03\x04" + raaka[4:])):
            polku.write_bytes(rikottu)
            try:
                lue(polku)
            except MuotoVirhe as e:
                print(f"{kuvaus}: {e}")
    return 0
# @loppu kaytto


if __name__ == "__main__":
    sys.exit(main())
