"""Stereonäkö: dispariteetti SGBM:llä ja syvyys Z = f B / d."""

import cv2
import numpy as np

# @alku kuvat
# Rektifioitu kuvapari: sama rivi kummassakin kuvassa, ja kohta, joka
# vasemmassa kuvassa on sarakkeessa x, on oikeassa sarakkeessa x - d.
# Näkymässä on kolme tasoa: tausta (d = 8), laatikko (d = 24) ja
# kiekko (d = 16). Kukin taso on täynnä satunnaista tekstuuria.
rng = np.random.default_rng(seed=17)
korkeus, leveys = 240, 320
tausta = np.full((korkeus, leveys), 255, np.uint8)
laatikko = np.zeros_like(tausta)
cv2.rectangle(laatikko, (60, 60), (150, 170), 255, -1)
kiekko = np.zeros_like(tausta)
cv2.circle(kiekko, (230, 120), 50, 255, -1)
tasot = [(8, tausta), (24, laatikko), (16, kiekko)]   # takaa eteen
tekstuurit = {d: cv2.GaussianBlur(
    rng.integers(0, 256, (korkeus, leveys + 64)).astype(np.uint8),
    (3, 3), 0) for d, _ in tasot}


def nakyma(oikea_kamera: bool) -> np.ndarray:
    kuva = np.zeros((korkeus, leveys), np.uint8)
    for d, maski in tasot:
        s = d if oikea_kamera else 0
        tekstuuri = tekstuurit[d]
        # Taso ja sen tekstuuri siirtyvät oikeassa kuvassa d px vasemmalle.
        pala = tekstuuri[:, 32 + s:32 + s + leveys]
        m = np.roll(maski, -s, axis=1) > 0
        kuva[m] = pala[m]
    return kuva


vasen, oikea = nakyma(False), nakyma(True)
# @loppu kuvat

# @alku sgbm
sgbm = cv2.StereoSGBM.create(minDisparity=0, numDisparities=32,
                             blockSize=5, P1=8 * 25, P2=32 * 25,
                             uniquenessRatio=10)
# SGBM palauttaa dispariteetin 16-kertaisena kokonaislukuna.
dispariteetti = sgbm.compute(vasen, oikea).astype(np.float32) / 16.0
f, B = 700.0, 120.0                     # polttoväli px, kantaväli mm
for nimi, (y, x), d_tosi in (("tausta", (30, 280), 8),
                             ("laatikko", (115, 105), 24),
                             ("kiekko", (120, 230), 16)):
    alue = dispariteetti[y - 10:y + 10, x - 10:x + 10]
    d = float(np.median(alue))
    print(f"{nimi:8s}: dispariteetti {d:5.1f} px (oikea {d_tosi}),"
          f" syvyys {f * B / d / 1000:4.2f} m"
          f" (oikea {f * B / d_tosi / 1000:4.2f} m)")
# @loppu sgbm
