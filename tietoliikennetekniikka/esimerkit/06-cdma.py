"""CDMA: käyttäjät erotetaan toisistaan ortogonaalisilla koodeilla."""

import numpy as np
import numpy.typing as npt


def walsh(n: int) -> npt.NDArray[np.int64]:
    """Hadamardin matriisi: rivit ovat keskenään ortogonaalisia."""
    h = np.array([[1]], dtype=np.int64)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    return h


# @alku cdma
koodit = walsh(8)[1:4]            # kolme käyttäjää, 8 sirua bittiä kohti
viestit = np.array([[1, -1, 1, 1],          # käyttäjä 1
                    [-1, -1, 1, -1],        # käyttäjä 2
                    [1, 1, -1, 1]])         # käyttäjä 3
# Jokainen bitti kerrotaan käyttäjän koodilla, ja signaalit summautuvat
# ilmassa samalla taajuudella ja samaan aikaan.
siruja = np.sum([np.kron(viestit[k], koodit[k]) for k in range(3)], axis=0)
rng = np.random.default_rng(2)
yhteinen = siruja + rng.normal(0, 0.8, siruja.shape)

for k in range(3):
    paloina = yhteinen.reshape(-1, 8)
    korrelaatio = paloina @ koodit[k] / 8
    arvio = np.sign(korrelaatio).astype(int)
    print(f"käyttäjä {k + 1}: korrelaatio {np.round(korrelaatio, 2)}"
          f" -> {arvio} oikein: {np.array_equal(arvio, viestit[k])}")
# @loppu cdma
