"""Sobel-gradientti: suuruus ja suunta käännetyn neliön reunoilla."""

import cv2
import numpy as np

# @alku gradientti
kuva = np.zeros((200, 200), np.uint8)
# Neliö, jota on käännetty 30 astetta: reunojen normaalit osoittavat
# suuntiin 30, 120, 210 ja 300 astetta.
laatikko = cv2.boxPoints(((100.0, 100.0), (100.0, 100.0), 30.0))
cv2.fillPoly(kuva, [np.round(laatikko).astype(np.int32)], 200)
sumea = cv2.GaussianBlur(kuva, (5, 5), 1.0)

gx = cv2.Sobel(sumea, cv2.CV_32F, 1, 0, ksize=3)   # d/dx liukulukuina
gy = cv2.Sobel(sumea, cv2.CV_32F, 0, 1, ksize=3)   # d/dy
suuruus, suunta = cv2.cartToPolar(gx, gy, angleInDegrees=True)
reuna = suuruus > 0.5 * float(suuruus.max())
print(f"reunapikseleitä {int(np.count_nonzero(reuna))}")
# Suuntahistogrammi 10 asteen lokeroihin, joiden keskikohdat ovat
# 0, 10, ..., 350 astetta. Painona on gradientin suuruus.
hist, _ = np.histogram((suunta[reuna] + 5) % 360, bins=36,
                       range=(0, 360), weights=suuruus[reuna])
huiput = sorted(10 * int(i) for i in np.argsort(hist)[-4:])
osuus = float(np.sort(hist)[-4:].sum() / hist.sum())
print("yleisimmät suunnat:", huiput, f"(osuus {100 * osuus:.0f} %)")
# @loppu gradientti

# @alku uint8
# Sudenkuoppa: uint8-tulos leikkaa negatiiviset derivaatat nollaan.
leikattu = cv2.Sobel(sumea, cv2.CV_8U, 1, 0, ksize=3)
print("CV_32F: negatiivisia", int(np.count_nonzero(gx < 0)),
      "/ CV_8U: negatiivisia mahdotonta, nollia",
      int(np.count_nonzero((leikattu == 0) & (gx < 0))))
# @loppu uint8
