"""Kulmat: Harris, Shi-Tomasi ja alipikselitarkkuus tunnetuilla kulmilla."""

import cv2
import numpy as np

# @alku kuva
# Shakkikuvio, jonka ruudun koko on 30 px ja ensimmäinen kulma kohdassa
# (20,25, 20,25). Kuva piirretään 8-kertaisena ja pienennetään
# INTER_AREA:lla, jolloin reunat osuvat alipikselikohtiin tarkasti.
s, ruutu, alku = 8, 30, 20.25
leveys, korkeus = 200, 170
yh, xh = np.mgrid[0:korkeus * s, 0:leveys * s]
# Suurennetun kuvan pikselin j keskikohta on alkuperäisessä kuvassa
# kohdassa (j + 0,5)/s - 0,5 (alkuperäisen pikselin keskikohta on
# kokonaisluku).
ax = np.floor(((xh + 0.5) / s - 0.5 - alku) / ruutu).astype(np.int64)
ay = np.floor(((yh + 0.5) / s - 0.5 - alku) / ruutu).astype(np.int64)
iso = np.where((ax + ay) % 2 == 0, 230, 25).astype(np.uint8)
kuva = cv2.resize(iso, (leveys, korkeus), interpolation=cv2.INTER_AREA)
oikeat = np.array([(alku + i * ruutu, alku + j * ruutu)
                   for j in range(6) for i in range(7)
                   if alku + j * ruutu < korkeus - 10
                   and alku + i * ruutu < leveys - 10], np.float32)
print(f"tunnettuja kulmia {len(oikeat)}")
# @loppu kuva

# @alku harris
vaste = cv2.cornerHarris(kuva.astype(np.float32), 5, 3, 0.04)
vahvat = vaste > 0.1 * float(vaste.max())
n_alueet = cv2.connectedComponents(vahvat.astype(np.uint8))[0] - 1
print(f"Harris: kulma-alueita {n_alueet}")
# @loppu harris

# @alku shitomasi
kulmat = cv2.goodFeaturesToTrack(kuva, maxCorners=50, qualityLevel=0.1,
                                 minDistance=10)
assert kulmat is not None
print(f"Shi-Tomasi: kulmia {len(kulmat)}")


def virhe(pisteet: np.ndarray) -> float:
    """Keskimääräinen etäisyys lähimpään tunnettuun kulmaan."""
    p = pisteet.reshape(-1, 1, 2) - oikeat.reshape(1, -1, 2)
    return float(np.linalg.norm(p, axis=2).min(axis=1).mean())


print(f"  kokonaislukupikselit: virhe {virhe(kulmat):.2f} px")
ehto = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
tarkat = cv2.cornerSubPix(kuva, kulmat.copy(), (5, 5), (-1, -1), ehto)
print(f"  cornerSubPix:         virhe {virhe(tarkat):.2f} px")
# @loppu shitomasi
