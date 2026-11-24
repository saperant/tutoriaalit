"""Pikaoppaan koodi: työkalun runko ja tavallisimmat kuviot."""

# @alku runko
import argparse
import logging
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

loki = logging.getLogger("tyokalu")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tyokalu")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("tiedostot", nargs="*", type=Path)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose
                        else logging.WARNING, stream=sys.stderr)
    loki.debug("argumentit %s", args)
    return 0
# @loppu runko


def esimerkit() -> None:
    # @alku re
    rivi = "UVM_ERROR @ 2us: [VERTAILU] odotettu 0x3f"
    m = re.match(r"UVM_(?P<taso>\w+) @ (?P<aika>\d+)(?P<yks>[munp]?s)",
                 rivi)
    assert m is not None
    print(m["taso"], int(m["aika"]), m["yks"])
    # @loppu re

    # @alku struct
    OTSAKE = struct.Struct("<4sHI")          # pieni-endian, tiivis
    raaka = OTSAKE.pack(b"MDAT", 1, 48000)
    print(OTSAKE.size, OTSAKE.unpack(raaka))
    print((0x0A15 >> 2) & 0b111)             # bitit 4:2
    # @loppu struct

    # @alku polut
    with tempfile.TemporaryDirectory() as tmp:
        juuri = Path(tmp)
        (juuri / "a" / "b").mkdir(parents=True)
        (juuri / "a" / "b" / "sim.log").write_text("ok\n", "utf-8")
        print([p.relative_to(juuri).as_posix()
               for p in sorted(juuri.rglob("*.log"))])
    # @loppu polut

    # @alku aliprosessi
    p = subprocess.run([sys.executable, "-c", "print('hei')"],
                       capture_output=True, text=True, timeout=10,
                       check=False)
    print(p.returncode, p.stdout.strip())
    # @loppu aliprosessi

    # @alku numpy
    x = np.array([0.1, 3.4, 2.9, 3.6, 0.2])
    yli = x > 3.0
    print(np.flatnonzero(yli), round(float(x.mean()), 2),
          np.flatnonzero(~yli[:-1] & yli[1:]) + 1)
    # @loppu numpy


if __name__ == "__main__":
    esimerkit()
    sys.exit(main([]))
