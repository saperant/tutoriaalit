"""Histogrammi, kontrastin venytys, tasoitus, CLAHE ja gammakorjaus."""

import cv2
import numpy as np

# @alku kuva
# Matalakontrastinen kuva: harmaasävyt vain välillä 90..150.
rng = np.random.default_rng(seed=7)
x = np.linspace(0, 1, 256, dtype=np.float32)
kuva = (90 + 60 * np.outer(x, x)).astype(np.uint8)
cv2.putText(kuva, "OCV", (40, 150), cv2.FONT_HERSHEY_SIMPLEX, 3,
            140, thickness=8)
kuva = np.clip(kuva + rng.normal(0, 2, kuva.shape), 0, 255)
kuva = kuva.astype(np.uint8)


def kuvaile(nimi: str, k: np.ndarray) -> None:
    hist = cv2.calcHist([k], [0], None, [256], [0, 256]).ravel()
    kaytossa = int(np.count_nonzero(hist))
    print(f"{nimi:14s} min {int(k.min()):3d}  max {int(k.max()):3d}"
          f"  keskihajonta {float(k.std()):5.1f}  tasoja {kaytossa:3d}")
# @loppu kuva


# @alku venytys
kuvaile("alkuperäinen", kuva)
venytetty = cv2.normalize(kuva, None, 0, 255, cv2.NORM_MINMAX)
kuvaile("venytys", venytetty)
tasoitettu = cv2.equalizeHist(kuva)
kuvaile("tasoitus", tasoitettu)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
kuvaile("CLAHE", clahe.apply(kuva))
# @loppu venytys


# @alku gamma
# Gammakorjaus hakutaulukolla: 256 arvoa lasketaan kerran, ja LUT
# soveltaa taulukkoa jokaiseen pikseliin.
def gamma_taulukko(gamma: float) -> np.ndarray:
    arvot = np.arange(256, dtype=np.float64) / 255.0
    return np.round(255.0 * arvot ** (1.0 / gamma)).astype(np.uint8)


for gamma in (0.5, 1.0, 2.2):
    korjattu = cv2.LUT(venytetty, gamma_taulukko(gamma))
    print(f"gamma {gamma:3.1f}: keskiarvo {float(korjattu.mean()):5.1f}")
# @loppu gamma
