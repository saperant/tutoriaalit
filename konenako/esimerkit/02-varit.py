"""Väriavaruudet: BGR-sudenkuoppa, HSV-kynnystys ja Lab-etäisyys."""

import cv2
import numpy as np
import numpy.typing as npt

# @alku bgr
# OpenCV tallentaa värikuvan kanavat järjestyksessä B, G, R.
punainen_rgb = np.array([[[255, 0, 0]]], np.uint8)   # RGB-ajattelulla
hsv = cv2.cvtColor(punainen_rgb, cv2.COLOR_BGR2HSV)
print("RGB-taulukko BGR:nä tulkittuna, sävy:", int(hsv[0, 0, 0]))
oikein = cv2.cvtColor(punainen_rgb, cv2.COLOR_RGB2HSV)
print("RGB-taulukko RGB:nä tulkittuna, sävy:", int(oikein[0, 0, 0]))
# @loppu bgr

# @alku hsv
# Pöydällä kolme värillistä kappaletta ja varjo, joka tummentaa
# oikeaa reunaa. HSV erottaa sävyn (H) kirkkaudesta (V).
kuva = np.full((100, 300, 3), (200, 200, 200), np.uint8)
cv2.circle(kuva, (50, 50), 30, (0, 0, 220), -1)      # punainen
cv2.circle(kuva, (150, 50), 30, (0, 200, 0), -1)     # vihreä
cv2.circle(kuva, (250, 50), 30, (0, 0, 220), -1)     # punainen
varjo = np.linspace(1.0, 0.45, 300, dtype=np.float32)[None, :, None]
kuva = (kuva * varjo).astype(np.uint8)
hsv_kuva = cv2.cvtColor(kuva, cv2.COLOR_BGR2HSV)
# Punainen on sävyn molemmissa päissä (0 ja 179), joten kaksi väliä.
ala = cv2.inRange(hsv_kuva, (0, 100, 50), (10, 255, 255))
yla = cv2.inRange(hsv_kuva, (170, 100, 50), (179, 255, 255))
maski = cv2.bitwise_or(ala, yla)
n, _, tilastot, _ = cv2.connectedComponentsWithStats(maski)
print("punaisia kappaleita:", n - 1,
      "alat:", tilastot[1:, cv2.CC_STAT_AREA].tolist())
bgr_maski = cv2.inRange(kuva, (0, 0, 150), (80, 80, 255))
print("sama BGR-rajoilla, kappaleita:",
      cv2.connectedComponentsWithStats(bgr_maski)[0] - 1)
# @loppu hsv


# @alku lab
# Lab-avaruudessa euklidinen etäisyys vastaa paremmin havaittua eroa.
def lab(bgr: tuple[int, int, int]) -> npt.NDArray[np.float32]:
    pikseli = np.array([[bgr]], np.float32) / 255.0
    return np.asarray(cv2.cvtColor(pikseli, cv2.COLOR_BGR2Lab)[0, 0],
                      np.float32)


pari_sininen = ((255, 0, 0), (255, 40, 0))     # sininen ja vähän vihreää
pari_vihrea = ((0, 160, 0), (0, 200, 0))       # kaksi vihreää
for nimi, (c1, c2) in (("siniset", pari_sininen),
                       ("vihreät", pari_vihrea)):
    bgr_ero = float(np.linalg.norm(np.subtract(c1, c2)))
    lab_ero = float(np.linalg.norm(lab(c1) - lab(c2)))
    print(f"{nimi}: BGR-ero {bgr_ero:5.1f}, Lab-ero {lab_ero:5.1f}")
# @loppu lab
