"""Morfologia: avaus poistaa roskat, sulkeminen täyttää aukot."""

import cv2
import numpy as np

# @alku kuva
# Binäärikuva: neljä suorakaidetta, niissä reikiä, ympärillä roskaa.
rng = np.random.default_rng(seed=8)
maski = np.zeros((160, 240), np.uint8)
for x in (20, 130):
    for y in (20, 90):
        cv2.rectangle(maski, (x, y), (x + 80, y + 50), 255, -1)
reiat = (rng.random(maski.shape) < 0.02) & (maski > 0)
roskat = (rng.random(maski.shape) < 0.01) & (maski == 0)
maski[reiat] = 0
maski[roskat] = 255
# @loppu kuva


# @alku operaatiot
def kuvaile(nimi: str, m: np.ndarray) -> None:
    n = cv2.connectedComponents(m)[0] - 1
    reikia = cv2.connectedComponents(cv2.bitwise_not(m))[0] - 2
    print(f"{nimi:22s} alueita {n:4d}, reikiä {reikia:4d},"
          f" pikseleitä {int(np.count_nonzero(m)):6d}")


rakenne = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
kuvaile("alkuperäinen", maski)
kuvaile("eroosio", cv2.erode(maski, rakenne))
kuvaile("dilataatio", cv2.dilate(maski, rakenne))
avattu = cv2.morphologyEx(maski, cv2.MORPH_OPEN, rakenne)
kuvaile("avaus", avattu)
kuvaile("avaus + sulkeminen",
        cv2.morphologyEx(avattu, cv2.MORPH_CLOSE, rakenne))
# @loppu operaatiot
