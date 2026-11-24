"""Sama reunaketju Pythonilla ja suorituskyvyn hinnat: silmukka vs. NumPy."""

import sys
import time

import cv2
import numpy as np


# @alku ketju
def synteettinen(leveys: int, korkeus: int) -> np.ndarray:
    """Sama kuva kuin C++-esimerkissä: 4 x 3 kiekkoa ja laatikkoa."""
    kuva = np.full((korkeus, leveys), 70, np.uint8)
    for i in range(12):
        x = (i % 4) * leveys // 4 + leveys // 8
        y = (i // 4) * korkeus // 3 + korkeus // 6
        if i % 2 == 0:
            cv2.circle(kuva, (x, y), 15 + i, 180, cv2.FILLED)
        else:
            cv2.rectangle(kuva, (x - 20, y - 15), (x + 20, y + 15), 30,
                          cv2.FILLED)
    return kuva


def reunat(kuva: np.ndarray) -> tuple[int, int]:
    sumea = cv2.GaussianBlur(kuva, (5, 5), 1.2)
    r = cv2.Canny(sumea, 30, 90)
    return cv2.countNonZero(r), cv2.connectedComponents(r)[0] - 1


cv2.setNumThreads(1)
kuva = synteettinen(640, 480)
pikselit, kayrat = reunat(kuva)
print(f"reunapikseleitä {pikselit}, reunakäyriä {kayrat}")
# @loppu ketju


# @alku hinnat
def laatikko_silmukka(k: np.ndarray) -> np.ndarray:
    """3 x 3 -keskiarvo pikseli kerrallaan Pythonin silmukoilla."""
    korkeus, leveys = k.shape
    tulos = np.zeros_like(k)
    for y in range(1, korkeus - 1):
        for x in range(1, leveys - 1):
            tulos[y, x] = int(k[y - 1:y + 2, x - 1:x + 2].sum()) // 9
    return tulos


def laatikko_numpy(k: np.ndarray) -> np.ndarray:
    """Sama vektoroituna: yhdeksän siirrettyä näkymää summataan."""
    s = np.zeros((k.shape[0] - 2, k.shape[1] - 2), np.int32)
    for dy in range(3):
        for dx in range(3):
            s += k[dy:dy + k.shape[0] - 2, dx:dx + k.shape[1] - 2]
    tulos = np.zeros_like(k)
    tulos[1:-1, 1:-1] = s // 9
    return tulos


pieni = kuva[:120, :160]
print("silmukka = NumPy:",
      bool(np.array_equal(laatikko_silmukka(pieni), laatikko_numpy(pieni))))
if "--mittaa" in sys.argv:          # ajat vaihtelevat koneittain
    for nimi, f in (("silmukka", laatikko_silmukka),
                    ("NumPy", laatikko_numpy),
                    ("OpenCV blur", lambda k: cv2.blur(k, (3, 3)))):
        alku = time.perf_counter()
        f(pieni)
        print(f"{nimi:12s} {1000 * (time.perf_counter() - alku):8.3f} ms")
# @loppu hinnat
