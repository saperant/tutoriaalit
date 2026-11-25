"""Lukee ARM64-ytimen Image-tiedoston 64 tavun otsakkeen.

Otsakkeen muoto on ytimen dokumentissa Documentation/arch/arm64/
booting.rst. Käynnistin (esim. U-Bootin booti) lukee samat kentät
ennen kuin hyppää ytimeen.

Käyttö: python3 otsake.py Image
"""

import os
import struct
import sys

# @alku otsake
MUOTO = "<IIQQQQQQII"  # little-endian: 2 x u32, 6 x u64, 2 x u32
SIVUKOOT = {0: "ei maaritelty", 1: "4 KiB", 2: "16 KiB", 3: "64 KiB"}


def tulkitse(otsake: bytes, tiedoston_koko: int) -> list[str]:
    (code0, _code1, text_offset, image_size, liput,
     _r2, _r3, _r4, taika, pe) = struct.unpack(MUOTO, otsake)
    alku = "MZ (EFI-tynka)" if code0 & 0xFFFF == 0x5A4D else "hyppykasky"
    kattaa = "kattaa tiedoston" if image_size >= tiedoston_koko else "pieni"
    return [
        f"taikaluku:     {taika.to_bytes(4, 'little')!r}",
        f"alku:          {alku}",
        f"text_offset:   {text_offset:#x}",
        f"tavujarjestys: {'big' if liput & 1 else 'little'}-endian",
        f"sivukoko:      {SIVUKOOT[(liput >> 1) & 3]}",
        f"image_size:    {kattaa}",
        f"PE-otsake:     {'on' if pe else 'ei'}",
    ]
# @loppu otsake


def main() -> int:
    if len(sys.argv) != 2:
        print("kaytto: otsake.py Image", file=sys.stderr)
        return 2
    with open(sys.argv[1], "rb") as f:
        otsake = f.read(struct.calcsize(MUOTO))
    for rivi in tulkitse(otsake, os.path.getsize(sys.argv[1])):
        print(rivi)
    return 0


if __name__ == "__main__":
    sys.exit(main())
