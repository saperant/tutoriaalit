"""Hamming(7,4): yhden bitin virheen korjaus."""

import numpy as np
import numpy.typing as npt

Bitit = npt.NDArray[np.uint8]

# @alku matriisit
# Generointimatriisi G ja tarkistusmatriisi H (systemaattinen muoto).
G = np.array([[1, 0, 0, 0, 1, 1, 0],
              [0, 1, 0, 0, 1, 0, 1],
              [0, 0, 1, 0, 0, 1, 1],
              [0, 0, 0, 1, 1, 1, 1]], dtype=np.uint8)
H = np.array([[1, 1, 0, 1, 1, 0, 0],
              [1, 0, 1, 1, 0, 1, 0],
              [0, 1, 1, 1, 0, 0, 1]], dtype=np.uint8)


def koodaa(data: Bitit) -> Bitit:
    return (data @ G % 2).astype(np.uint8)


def korjaa(sana: Bitit) -> Bitit:
    """Syndrooma on virheellisen bitin sarake H:ssa."""
    syndrooma = H @ sana % 2
    if syndrooma.any():
        sarake = int(np.flatnonzero((syndrooma == H.T).all(axis=1))[0])
        sana = sana.copy()
        sana[sarake] ^= 1
    return sana[:4]
# @loppu matriisit


data = np.array([1, 0, 1, 1], dtype=np.uint8)
sana = koodaa(data)
virheellinen = sana.copy()
virheellinen[5] ^= 1
print("data", data, "koodisana", sana)
print("virhe bitissä 5, korjattu:", korjaa(virheellinen))

# @alku simulaatio
# Binäärinen symmetrinen kanava, bittivirhetodennäköisyys p.
rng = np.random.default_rng(3)
lohkoja = 100_000
print("lohkovirheiden osuus:")
for p in (0.01, 0.001):
    datat = rng.integers(0, 2, (lohkoja, 4), dtype=np.uint8)
    sanat = datat @ G % 2
    kohina = (rng.random((lohkoja, 7)) < p).astype(np.uint8)
    vastaanotetut = (sanat + kohina) % 2
    oikein = sum(np.array_equal(korjaa(v), d)
                 for v, d in zip(vastaanotetut, datat, strict=True))
    koodaamaton = 1 - (1 - p) ** 4
    koodattu = 1 - ((1 - p) ** 7 + 7 * p * (1 - p) ** 6)
    print(f"p={p}: ilman koodia {koodaamaton:.1e},"
          f" Hamming {koodattu:.1e} (simuloitu"
          f" {1 - oikein / lohkoja:.1e})")
# @loppu simulaatio
