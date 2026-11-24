"""Kuva on NumPy-taulukko: muoto, indeksointi, näkymät ja ylivuoto."""

import cv2
import numpy as np

# @alku muoto
kuva = np.zeros((120, 160, 3), np.uint8)       # korkeus, leveys, kanavat
cv2.rectangle(kuva, (40, 20), (99, 49), (255, 0, 0), thickness=-1)
print(f"muoto {kuva.shape}, tyyppi {kuva.dtype}, tavuja {kuva.nbytes}")
# Indeksi on [rivi, sarake] eli [y, x]; OpenCV:n pisteet ovat (x, y).
print("kuva[30, 50] =", kuva[30, 50].tolist())   # suorakaiteen sisällä
print("kuva[50, 30] =", kuva[50, 30].tolist())   # ulkopuolella
# @loppu muoto

# @alku nakyma
alue = kuva[20:50, 40:100]          # näkymä: jakaa muistin kuvan kanssa
alue[:] = (0, 0, 255)
print("näkymän muutos näkyy kuvassa:", kuva[30, 50].tolist())
kopio = kuva[20:50, 40:100].copy()  # oma muisti
kopio[:] = 0
print("kopion muutos ei näy kuvassa:", kuva[30, 50].tolist())
# @loppu nakyma

# @alku ylivuoto
a = np.array([[200, 250]], np.uint8)
b = np.array([[100, 10]], np.uint8)
print("NumPy  a + b:", (a + b).tolist())         # kiertää modulo 256
print("OpenCV add  :", cv2.add(a, b).tolist())   # saturoi 255:een
print("NumPy  b - a:", (b - a).tolist())
print("OpenCV sub  :", cv2.subtract(b, a).tolist())
# Laskenta liukuluvuilla ja paluu uint8:ksi hallitusti:
summa = np.clip(a.astype(np.float32) + b, 0, 255).astype(np.uint8)
print("float + clip:", summa.tolist())
# @loppu ylivuoto
