"""Isännän puoli kehysprotokollasta (laite: 03-kehykset/main.c).

    python3 kehykset.py tuota <tiedosto>  isännän tavut laitteelle
    python3 kehykset.py pura <tiedosto>   laitteen vastausten purku
"""

import sys
from pathlib import Path

from mallit.kehys import kehys, pura_virta

KAIKU, SUMMA, LOPPU = 0x01, 0x02, 0x7F
SYYT = {1: "CRC", 2: "COBS", 3: "pituus", 4: "komento"}


# @alku tuota
def istunto() -> bytes:
    """Komentosarja, jossa on mukana tahallisia virheitä."""
    rikki = bytearray(kehys(bytes([KAIKU]) + b"rikki"))
    rikki[3] ^= 0x01  # yksi bitti kääntyy siirrossa
    return b"".join([
        kehys(bytes([KAIKU]) + b"hei"),
        kehys(bytes([SUMMA, 1, 2, 3, 250])),
        bytes(rikki),
        bytes([0x13, 0x37, 0x00]),  # häiriötä linjalla
        kehys(bytes([KAIKU]) + bytes(range(1, 41))),  # liian pitkä
        kehys(bytes([0x42])),  # tuntematon komento
        kehys(bytes([KAIKU]) + b"taas"),
        kehys(bytes([LOPPU])),
    ])
# @loppu tuota


# @alku pura
def kuvaa(vastaus: bytes | str) -> str:
    if isinstance(vastaus, str):
        return f"virheellinen vastaus: {vastaus}"
    komento, data = vastaus[0], vastaus[1:]
    if komento == 0xEE:
        return f"NAK, syy {SYYT.get(data[0], '?')}"
    if komento == KAIKU | 0x80:
        return f"kaiku {data.decode('ascii')!r}"
    if komento == SUMMA | 0x80:
        return f"summa {int.from_bytes(data, 'big')}"
    if komento == LOPPU | 0x80:
        return "loppu"
    return f"tuntematon vastaus {vastaus.hex()}"
# @loppu pura


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("tuota", "pura"):
        print(__doc__, file=sys.stderr)
        return 2
    polku = Path(sys.argv[2])
    if sys.argv[1] == "tuota":
        polku.write_bytes(istunto())
        return 0
    for i, vastaus in enumerate(pura_virta(polku.read_bytes()), 1):
        print(f"vastaus {i}: {kuvaa(vastaus)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
