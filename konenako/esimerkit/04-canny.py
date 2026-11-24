"""Canny: kynnysten vaikutus ja vertailu tunnettuun ääriviivaan."""

import cv2
import numpy as np

# @alku kuva
rng = np.random.default_rng(seed=4)
puhdas = np.full((200, 200), 80, np.uint8)
cv2.circle(puhdas, (100, 100), 60, 170, -1)
kohinainen = np.clip(puhdas + rng.normal(0, 18, puhdas.shape), 0, 255)
kuva = kohinainen.astype(np.uint8)
# Totuus: ympyrän reuna ja sen ympärillä kahden pikselin toleranssi.
totuus = np.zeros_like(puhdas)
cv2.circle(totuus, (100, 100), 60, 255, thickness=1)
toleranssi = cv2.dilate(totuus, np.ones((5, 5), np.uint8))
# @loppu kuva


# @alku arvio
def arvioi(reunat: np.ndarray) -> tuple[float, float]:
    """Tarkkuus (reunoista oikeita) ja saanti (ympyrästä löytyi)."""
    loydetyt = reunat > 0
    oikeat = np.count_nonzero(loydetyt & (toleranssi > 0))
    tarkkuus = oikeat / max(1, int(np.count_nonzero(loydetyt)))
    laajennettu = cv2.dilate(reunat, np.ones((5, 5), np.uint8))
    saanti = np.count_nonzero((totuus > 0) & (laajennettu > 0))
    return tarkkuus, saanti / int(np.count_nonzero(totuus))


sumea = cv2.GaussianBlur(kuva, (0, 0), 2.0)
for nimi, lahde, ala, yla in (("ei tasoitusta", kuva, 50, 100),
                              ("tasoitus", sumea, 10, 30),
                              ("tasoitus", sumea, 30, 90),
                              ("tasoitus", sumea, 170, 170),
                              ("tasoitus", sumea, 60, 170)):
    reunat = cv2.Canny(lahde, ala, yla)
    t, s = arvioi(reunat)
    print(f"{nimi:13s} kynnykset {ala:3d}/{yla:3d}:"
          f" tarkkuus {100 * t:5.1f} %, saanti {100 * s:5.1f} %")
# @loppu arvio
