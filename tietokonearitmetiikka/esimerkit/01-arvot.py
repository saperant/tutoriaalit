"""Samat arvot Pythonissa: int on rajaton, float on binary64."""

import struct

# @alku tavut
print((1000).to_bytes(4, "little").hex(" "))
print((-1).to_bytes(4, "little", signed=True).hex(" "))
print(struct.pack("<f", 0.1).hex(" "))       # binary32
print(struct.pack("<d", 0.1).hex(" "))       # binary64
print(0.1 + 0.2 == 0.3, 0.1 + 0.2)
print(2**100, (2**100).bit_length())
# @loppu tavut
