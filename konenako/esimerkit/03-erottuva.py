"""Erottuva ydin: Gaussin suodin kahtena 1D-suodatuksena."""

import cv2
import numpy as np

# @alku ydin
sigma = 2.0
koko = 2 * int(np.ceil(3 * sigma)) + 1          # 3 sigmaa kumpaankin
g = cv2.getGaussianKernel(koko, sigma)            # koko x 1, summa 1
ydin_2d = g @ g.T                                 # ulkotulo: koko x koko
print(f"sigma {sigma}: ydin {koko} x {koko}, summa {float(g.sum()):.3f}")
print("1D-ytimen keskiosa:", " ".join(f"{v:.3f}" for v in g[4:9, 0]))
# Ydin on erottuva, jos sen aste (rank) on 1.
print("2D-ytimen aste:", int(np.linalg.matrix_rank(ydin_2d)))
# @loppu ydin

# @alku vertailu
rng = np.random.default_rng(seed=5)
kuva = rng.uniform(0, 255, (200, 300)).astype(np.float32)
suora = cv2.filter2D(kuva, -1, ydin_2d)
erotettu = cv2.sepFilter2D(kuva, -1, g, g)
valmis = cv2.GaussianBlur(kuva, (koko, koko), sigma)
print("sepFilter2D = filter2D:",
      bool(np.allclose(suora, erotettu, atol=1e-3)))
print("GaussianBlur = filter2D:",
      bool(np.allclose(suora, valmis, atol=1e-3)))
pikseleita = kuva.size
suora_lkm = f"{pikseleita * koko * koko:_}".replace("_", " ")
erotettu_lkm = f"{pikseleita * 2 * koko:_}".replace("_", " ")
print(f"kertolaskuja: 2D {suora_lkm}, erotettu {erotettu_lkm}")
# @loppu vertailu
