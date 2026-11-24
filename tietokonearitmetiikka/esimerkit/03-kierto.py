"""Pythonin int ei vuoda yli; kiinteän leveyden aritmetiikka emuloidaan."""

import numpy as np


# @alku emulointi
def int32(x: int) -> int:
    """Tulkitsee x:n 32-bittisenä kahden komplementin lukuna."""
    return (x + 2**31) % 2**32 - 2**31


print(int32(2**31 - 1 + 1), int32(0xFFFF_FFFF), int32(-(2**31) - 1))
# @loppu emulointi

# @alku numpy
summat = np.array([900_000_000] * 3, dtype=np.int32)
print(summat.sum(dtype=np.int32))       # kiertää hiljaa
print(summat.sum(dtype=np.int64))       # leveämpi kertymä
print(int(summat[0]) * 3)               # Pythonin int
# @loppu numpy
