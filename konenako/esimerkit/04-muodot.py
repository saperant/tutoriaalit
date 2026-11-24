"""Ääriviivat ja muotoanalyysi: monikulmiot, pyöreys ja Hu-momentit."""

import cv2
import numpy as np

# @alku kuva
kuva = np.zeros((200, 400), np.uint8)
cv2.circle(kuva, (60, 100), 45, 255, -1)
cv2.rectangle(kuva, (130, 55), (220, 145), 255, -1)
kolmio = np.array([[250, 150], [340, 150], [295, 60]], np.int32)
cv2.fillPoly(kuva, [kolmio], 255)
cv2.ellipse(kuva, (370, 100), (20, 60), 0, 0, 360, 255, -1)
# @loppu kuva

# @alku ariviivat
ariviivat, _ = cv2.findContours(kuva, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
for c in sorted(ariviivat, key=lambda c: cv2.boundingRect(c)[0]):
    ala = cv2.contourArea(c)
    piiri = cv2.arcLength(c, closed=True)
    pyoreys = 4 * np.pi * ala / piiri**2          # ympyrä 1, viiva 0
    kulmat = len(cv2.approxPolyDP(c, 0.02 * piiri, closed=True))
    x, y, w, h = cv2.boundingRect(c)
    if kulmat == 3:
        muoto = "kolmio"
    elif kulmat == 4:
        muoto = "nelikulmio"
    elif pyoreys > 0.85:
        muoto = "ympyrä"
    else:
        muoto = "soikio"
    print(f"x={x:3d}: {muoto:10s} kulmia {kulmat:2d},"
          f" pyöreys {pyoreys:.2f}, kuvasuhde {w / h:.2f}")
# @loppu ariviivat


# @alku hu
# Hu-momentit eivät muutu siirrossa, skaalauksessa eikä kierrossa.
def hu(maski: np.ndarray) -> np.ndarray:
    h = cv2.HuMoments(cv2.moments(maski, binaryImage=True)).ravel()
    return -np.sign(h) * np.log10(np.abs(h))     # tavallinen log-asteikko


pohja = np.zeros((300, 300), np.uint8)
cv2.fillPoly(pohja, [kolmio - [150, 0]], 255)
kierto = cv2.getRotationMatrix2D((150, 150), 40, 1.5)
muunnettu = cv2.warpAffine(pohja, kierto, (300, 300))
print("Hu 1-3:", " ".join(f"{v:.1f}" for v in hu(pohja)[:3]))
ero = float(np.abs(hu(pohja)[:4] - hu(muunnettu)[:4]).max())
print("kierto 40 astetta ja skaalaus 1,5: Hu 1-4 muuttuu alle 0,05:",
      ero < 0.05)
# @loppu hu
