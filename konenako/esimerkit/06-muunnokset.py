"""Affiiniset muunnokset ja interpoloinnin kertyvä virhe."""

import cv2
import numpy as np

# @alku affiini
# Kolme pisteparia määrää affiinisen muunnoksen (6 vapausastetta).
lahto = np.array([[0, 0], [100, 0], [0, 50]], np.float32)
kohde = np.array([[20, 30], [106.6, 80], [-5, 73.3]], np.float32)
A = cv2.getAffineTransform(lahto, kohde)
print("A =")
for rivi in A:
    print("  ", " ".join(f"{v:8.3f}" for v in rivi))
kaanteinen = cv2.invertAffineTransform(A)
takaisin = cv2.transform(kohde[None], kaanteinen)[0]
print("käänteismuunnos palauttaa pisteet:",
      bool(np.allclose(takaisin, lahto, atol=1e-3)))
# @loppu affiini

# @alku kertyva
# Kuvaa kierretään 12 kertaa 30 astetta, eli yhteensä täysi kierros.
# Jokainen kierto interpoloi uudelleen, ja virhe kertyy.
rng = np.random.default_rng(seed=9)
kuva = np.zeros((200, 200), np.uint8)
for _ in range(40):
    x, y = (int(v) for v in rng.integers(40, 160, size=2))
    sade, savy = int(rng.integers(3, 12)), int(rng.integers(50, 256))
    cv2.circle(kuva, (x, y), sade, savy, -1)
kierto = cv2.getRotationMatrix2D((99.5, 99.5), 30, 1.0)
keskusta = np.s_[50:150, 50:150]                  # reunat ulos rajauksesta
for nimi, tapa in (("INTER_NEAREST", cv2.INTER_NEAREST),
                   ("INTER_LINEAR", cv2.INTER_LINEAR),
                   ("INTER_CUBIC", cv2.INTER_CUBIC),
                   ("INTER_LANCZOS4", cv2.INTER_LANCZOS4)):
    tulos: np.ndarray = kuva.copy()
    for _ in range(12):
        tulos = cv2.warpAffine(tulos, kierto, (200, 200), flags=tapa)
    psnr = cv2.PSNR(kuva[keskusta], tulos[keskusta])
    print(f"{nimi:15s} PSNR täyden kierroksen jälkeen {psnr:5.1f} dB")
# @loppu kertyva
