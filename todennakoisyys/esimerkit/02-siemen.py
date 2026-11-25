"""Siemen ja generaattoriolio: toistettava simulaatio."""

import numpy as np

# @alku siemen
# Generaattori on olio, jonka tila määräytyy siemenestä. Sama siemen
# tuottaa saman lukujonon joka ajolla ja jokaisella koneella.
a = np.random.default_rng(2026).integers(1, 7, size=8)
b = np.random.default_rng(2026).integers(1, 7, size=8)
c = np.random.default_rng(2027).integers(1, 7, size=8)
print("siemen 2026:", a.tolist())
print("siemen 2026:", b.tolist())
print("siemen 2027:", c.tolist())

# Generaattori välitetään funktioille parametrina. Globaalia tilaa ei
# ole, joten kaksi simulaatiota eivät sotke toistensa lukujonoja.


def kutosia(rng: np.random.Generator, heittoja: int) -> int:
    return int(np.sum(rng.integers(1, 7, size=heittoja) == 6))


rng = np.random.default_rng(2026)
print("kutosia 600 heitossa:", kutosia(rng, 600), "ja", kutosia(rng, 600))
# @loppu siemen
