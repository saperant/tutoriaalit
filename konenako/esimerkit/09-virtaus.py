"""Optinen virtaus: Lucas-Kanade tunnetulla synteettisellä liikkeellä."""

import cv2
import numpy as np

# @alku kuvat
# Teksturoitu kuva ja sama kuva siirrettynä (3,4 px, -1,8 px) eli
# alipikselin tarkkuudella: tunnettu liike, jota virtauksen pitää mitata.
rng = np.random.default_rng(seed=23)
kohina = rng.integers(0, 256, (240, 320)).astype(np.uint8)
kuva1 = cv2.GaussianBlur(kohina, (0, 0), 2.0)
liike = np.array([3.4, -1.8])
siirto = np.array([[1, 0, liike[0]], [0, 1, liike[1]]], np.float32)
kuva2 = cv2.warpAffine(kuva1, siirto, (320, 240), flags=cv2.INTER_CUBIC,
                       borderMode=cv2.BORDER_REFLECT)
# @loppu kuvat

# @alku lk
pisteet = cv2.goodFeaturesToTrack(kuva1, maxCorners=200,
                                  qualityLevel=0.01, minDistance=8)
assert pisteet is not None
seuratut, tila, _ = cv2.calcOpticalFlowPyrLK(
    kuva1, kuva2, pisteet, None, winSize=(21, 21), maxLevel=2)
ok = tila.ravel() == 1
siirtymat = (seuratut - pisteet).reshape(-1, 2)[ok]
arvio = np.median(siirtymat, axis=0)
print(f"seurattuja pisteitä yli 90 %: {ok.mean() > 0.9}")
print(f"mediaaniliike ({arvio[0]:5.2f}, {arvio[1]:5.2f}) px,"
      f" oikea ({liike[0]:5.2f}, {liike[1]:5.2f}) px")
print(f"virhe alle 0,1 px: {float(np.linalg.norm(arvio - liike)) < 0.1}")
# @loppu lk
