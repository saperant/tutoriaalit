"""Binääristen tietueiden lukeminen suoraan NumPy-taulukoksi.

Logiikka-analysaattori tallentaa tapahtumat 8 tavun tietueina:
aikaleima (u32, ns), kanava (u8), liput (u8) ja arvo (i16), pieni-
endian. struct-silmukka toimisi, mutta miljoonilla tietueilla
rakenteinen dtype ja frombuffer ovat moninkertaisesti nopeampia, koska
dataa ei kopioida eikä käsitellä Pythonissa tietue kerrallaan.
"""

import struct

import numpy as np

# @alku dtype
TIETUE = np.dtype([("aika_ns", "<u4"), ("kanava", "u1"),
                   ("liput", "u1"), ("arvo", "<i2")])
assert TIETUE.itemsize == 8
# @loppu dtype

# Esimerkkidata: samat tavut kuin laitteen tiedostossa.
raaka = b"".join(struct.pack("<IBBh", *tietue) for tietue in [
    (0, 0, 0, 0), (125, 1, 1, 512), (250, 0, 0, -12),
    (375, 1, 0, 515), (500, 1, 3, 2047), (625, 0, 0, -10)])

# @alku lue
tapahtumat = np.frombuffer(raaka, dtype=TIETUE)   # ei kopiota
print(tapahtumat.size, "tapahtumaa")
kanava1 = tapahtumat[tapahtumat["kanava"] == 1]
print("kanava 1 arvot:", kanava1["arvo"])
print("aikavälit:", np.diff(kanava1["aika_ns"]), "ns")
ylivuoto = (tapahtumat["liput"] & 0b10) != 0       # lippubitti 1
print("ylivuoto ajanhetkillä:", tapahtumat["aika_ns"][ylivuoto])
print("vain luku:", not tapahtumat.flags.writeable)
# @loppu lue
