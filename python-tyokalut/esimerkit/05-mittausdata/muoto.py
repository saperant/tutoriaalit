"""MDAT-mittausdatatiedosto: usean kanavan 16-bittiset näytteet.

Rakenne (kaikki pieni-endian):

  otsake  4 s  taikasana b"MDAT"
          u16  versio (1)
          u16  kanavien määrä
          u32  näytetaajuus (Hz)
          u32  näytteiden määrä kanavaa kohden
  data    i16  näytteet lomitettuina: k0 k1 ... k0 k1 ...
  loppu   u32  CRC-32 otsakkeesta ja datasta
"""

import array
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

# @alku muoto
TAIKA = b"MDAT"
VERSIO = 1
OTSAKE = struct.Struct("<4sHHII")
CRC = struct.Struct("<I")


class MuotoVirhe(ValueError):
    """Tiedosto ei ole kelvollinen MDAT-tiedosto."""
# @loppu muoto


# @alku kirjoita
def kirjoita(polku: Path, taajuus: int, kanavat: list[list[int]]) -> None:
    pituudet = {len(k) for k in kanavat}
    if len(pituudet) != 1:
        raise ValueError("kanavissa on eri määrä näytteitä")
    n = pituudet.pop()
    otsake = OTSAKE.pack(TAIKA, VERSIO, len(kanavat), taajuus, n)
    lomitettu = array.array("h", (k[i] for i in range(n) for k in kanavat))
    if sys.byteorder == "big":
        lomitettu.byteswap()            # tiedostossa aina pieni-endian
    data = lomitettu.tobytes()
    crc = zlib.crc32(data, zlib.crc32(otsake))
    polku.write_bytes(otsake + data + CRC.pack(crc))
# @loppu kirjoita


@dataclass(frozen=True)
class Mittaus:
    taajuus: int
    kanavia: int
    naytteita: int
    _naytteet: memoryview

    def kanava(self, i: int) -> list[int]:
        return self._naytteet[i::self.kanavia].tolist()


# @alku lue
def lue(polku: Path) -> Mittaus:
    raaka = memoryview(polku.read_bytes())   # viipaleet eivät kopioi
    if len(raaka) < OTSAKE.size + CRC.size:
        raise MuotoVirhe("tiedosto on liian lyhyt")
    taika, versio, kanavia, taajuus, n = OTSAKE.unpack(
        raaka[:OTSAKE.size])
    if taika != TAIKA:
        raise MuotoVirhe(f"väärä taikasana {bytes(taika)!r}")
    if versio != VERSIO:
        raise MuotoVirhe(f"tuntematon versio {versio}")
    odotettu = OTSAKE.size + 2 * kanavia * n + CRC.size
    if len(raaka) != odotettu:
        raise MuotoVirhe(f"pituus {len(raaka)}, odotettiin {odotettu}")
    (crc,) = CRC.unpack(raaka[-CRC.size:])
    if zlib.crc32(raaka[:-CRC.size]) != crc:
        raise MuotoVirhe("tarkistussumma ei täsmää")
    data = raaka[OTSAKE.size:-CRC.size]
    if sys.byteorder == "big":
        naytteet = array.array("h", data)
        naytteet.byteswap()
        return Mittaus(taajuus, kanavia, n, memoryview(naytteet))
    return Mittaus(taajuus, kanavia, n, data.cast("h"))
# @loppu lue
