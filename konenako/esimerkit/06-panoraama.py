"""Panoraaman periaate: piirteet, homografia ja kuvien yhdistäminen."""

import cv2
import numpy as np

# @alku kuvat
# Leveä näkymä, josta otetaan kaksi limittäistä "valokuvaa". Oikea
# kuva on otettu hieman eri suunnasta: sitä on vääristetty tunnetulla
# homografialla.
rng = np.random.default_rng(seed=31)
nakyma = np.full((300, 700), 110, np.uint8)
for _ in range(150):
    x, y = int(rng.integers(0, 700)), int(rng.integers(0, 300))
    koko, savy = int(rng.integers(4, 20)), int(rng.integers(0, 256))
    cv2.circle(nakyma, (x, y), koko, savy, -1)
vasen = nakyma[:, :450].copy()
H_oikea = np.array([[1.0, 0.02, -250.0], [0.01, 1.0, 5.0],
                    [2e-5, 0.0, 1.0]])            # näkymä -> oikea kuva
oikea = cv2.warpPerspective(nakyma, H_oikea, (400, 300))
# @loppu kuvat

# @alku yhdistys
orb = cv2.ORB.create(nfeatures=2000)
kp1, d1 = orb.detectAndCompute(vasen, None)
kp2, d2 = orb.detectAndCompute(oikea, None)
parit = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(d2, d1, k=2)
hyvat = [p[0] for p in parit
         if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
a = np.array([kp2[m.queryIdx].pt for m in hyvat], np.float32)
b = np.array([kp1[m.trainIdx].pt for m in hyvat], np.float32)
cv2.setRNGSeed(1)
H, maski = cv2.findHomography(a, b, cv2.RANSAC, 2.0)   # oikea -> vasen
print(f"pareja yli 100 {len(hyvat) > 100},"
      f" RANSAC hyväksyi yli 60 % {float(maski.mean()) > 0.6}")

# Oikea kuva vasemman koordinaatistoon 700 px leveälle kankaalle.
kangas = cv2.warpPerspective(oikea, H, (700, 300))
peitto = cv2.warpPerspective(np.full_like(oikea, 255), H, (700, 300))
kangas[:, :450] = np.where(peitto[:, :450] > 0, kangas[:, :450], vasen)
# Tarkistus: yhdistetty kuva verrataan alkuperäiseen näkymään alueella,
# jonka oikea kuva peittää (reunoilta 3 px pois interpoloinnin takia).
sisalla = cv2.erode(peitto, np.ones((7, 7), np.uint8)) > 0
ero = np.abs(kangas.astype(np.int16) - nakyma.astype(np.int16))[sisalla]
print(f"keskimääräinen ero alkuperäiseen alle 5 harmaasävyä:"
      f" {float(ero.mean()) < 5}")
# @loppu yhdistys
