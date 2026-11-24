"""binary64, binary32 ja binary16 kenttinä struct-moduulilla."""

import struct
from decimal import Decimal
from fractions import Fraction

MUODOT = {  # nimi: (struct-koodi, eksponenttibitit, mantissabitit)
    "binary64": ("<d", 11, 52),
    "binary32": ("<f", 8, 23),
    "binary16": ("<e", 5, 10),
}


# @alku kentat
def kentat(x: float, muoto: str) -> tuple[int, int, int, float]:
    """Palauttaa etumerkin, eksponentin, mantissan ja pyöristetyn arvon."""
    koodi, e_bitit, m_bitit = MUODOT[muoto]
    tavut = struct.pack(koodi, x)            # pyöristys muotoon
    b = int.from_bytes(tavut, "little")
    m = b & ((1 << m_bitit) - 1)
    e = (b >> m_bitit) & ((1 << e_bitit) - 1)
    s = b >> (m_bitit + e_bitit)
    return s, e, m, struct.unpack(koodi, tavut)[0]
# @loppu kentat


for muoto in MUODOT:
    s, e, m, arvo = kentat(0.1, muoto)
    bias = 2 ** (MUODOT[muoto][1] - 1) - 1
    print(f"{muoto}: s={s} e={e - bias:+d} m={m:#x} arvo={arvo!r}")
# @alku tarkka
print(Decimal(0.1))                 # tallennetun luvun tarkka arvo
print(Fraction(0.1), (0.1).hex())
print(Decimal(struct.unpack("<f", struct.pack("<f", 0.1))[0]))
# @loppu tarkka
