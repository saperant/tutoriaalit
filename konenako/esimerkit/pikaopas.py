"""Pikaoppaan OpenCV-reseptit: kuva, suodatus, piirteet ja geometria."""

import cv2
import numpy as np

kuva = np.zeros((240, 320, 3), np.uint8)
cv2.rectangle(kuva, (60, 50), (200, 170), (40, 160, 220), -1)

# @alku kuva
harmaa = cv2.cvtColor(kuva, cv2.COLOR_BGR2GRAY)      # BGR, ei RGB!
hsv = cv2.cvtColor(kuva, cv2.COLOR_BGR2HSV)          # H 0..179
liuku = harmaa.astype(np.float32) / 255.0             # laske liukuluvuin
takaisin = np.clip(liuku * 255.0, 0, 255).astype(np.uint8)
alue = kuva[50:170, 60:200]                           # [y, x], näkymä
_, maski = cv2.threshold(harmaa, 0, 255,
                         cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# @loppu kuva

# @alku suodatus
sumea = cv2.GaussianBlur(harmaa, (0, 0), sigmaX=2.0)
mediaani = cv2.medianBlur(harmaa, 5)                  # suola ja pippuri
gx = cv2.Sobel(harmaa, cv2.CV_32F, 1, 0)              # ei uint8:aa!
reunat = cv2.Canny(sumea, 30, 90)
avattu = cv2.morphologyEx(maski, cv2.MORPH_OPEN,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                    (5, 5)))
n, nimiot, tilastot, keskipisteet = cv2.connectedComponentsWithStats(
    avattu)
# @loppu suodatus

# @alku piirteet
orb = cv2.ORB.create(nfeatures=500)
kp, kuvaajat = orb.detectAndCompute(harmaa, None)
kulmat = cv2.goodFeaturesToTrack(harmaa, 20, 0.05, 10)
ariviivat, hierarkia = cv2.findContours(maski, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
# @loppu piirteet

# @alku geometria
A = cv2.getRotationMatrix2D((160, 120), angle=30, scale=1.0)
kierretty = cv2.warpAffine(kuva, A, (320, 240), flags=cv2.INTER_LINEAR)
pienempi = cv2.resize(kuva, None, fx=0.5, fy=0.5,
                      interpolation=cv2.INTER_AREA)   # pienennys: AREA
lahde = np.array([[0, 0], [319, 0], [319, 239], [0, 239]], np.float32)
kohde = np.array([[10, 5], [300, 20], [310, 230], [5, 220]], np.float32)
H = cv2.getPerspectiveTransform(lahde, kohde)
oikaistu = cv2.warpPerspective(kuva, H, (320, 240))
# @loppu geometria

print(harmaa.shape, hsv.shape, alue.shape, int(n), len(ariviivat),
      kierretty.shape, pienempi.shape, oikaistu.shape)
