"""Otsakkeen kenttien tulkinta: jokainen 4 tavun sana usealla tavalla.

Käyttö: python3 sanat.py TIEDOSTO ALKU LOPPU

Sarakkeet: siirtymä, sana heksana (little endian), kymmenjärjestelmässä,
kahtena 16-bittisenä lukuna ja tavuina ASCII-merkkeinä.
"""
import struct
import sys


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    alku, loppu = int(sys.argv[2], 0), int(sys.argv[3], 0)
    for o in range(alku, loppu, 4):
        sana, = struct.unpack_from("<I", data, o)
        ala, yla = struct.unpack_from("<HH", data, o)
        ascii_ = "".join(chr(t) if 0x20 <= t < 0x7F else "."
                         for t in data[o:o + 4])
        rivi = f"{o:04x}  {sana:08x}  {sana:10}  {ala:5} {yla:5}  {ascii_}"
        print(rivi.rstrip())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
