"""Kameran kalibrointi synteettisillä shakkilautakuvilla."""

import cv2
import numpy as np

from kamera import Kamera, Lauta, asennot, renderoi

# @alku kalibrointi
oikea = Kamera()
lauta = Lauta()
kuvio = (lauta.sarakkeet, lauta.rivit)
ehto = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 1e-4)
kohdepisteet, kuvapisteet = [], []
for rvec, tvec in asennot():
    kuva = renderoi(oikea, lauta, rvec, tvec)
    loytyi, kulmat = cv2.findChessboardCorners(kuva, kuvio)
    if not loytyi:
        continue
    kulmat = cv2.cornerSubPix(kuva, kulmat, (7, 7), (-1, -1), ehto)
    kohdepisteet.append(lauta.kulmat().astype(np.float32))
    kuvapisteet.append(kulmat)
print(f"lauta löytyi {len(kuvapisteet)} kuvasta 10:stä")

virhe, K, d, _, _ = cv2.calibrateCamera(
    kohdepisteet, kuvapisteet, (oikea.leveys, oikea.korkeus), None, None,
    flags=cv2.CALIB_FIX_K3 + cv2.CALIB_ZERO_TANGENT_DIST)
print(f"uudelleenprojektiovirhe alle 0,1 px: {virhe < 0.1}")
for nimi, arvio, tosi, raja in (
        ("fx", K[0, 0], oikea.fx, 2.0), ("fy", K[1, 1], oikea.fy, 2.0),
        ("cx", K[0, 2], oikea.cx, 2.0), ("cy", K[1, 2], oikea.cy, 2.0),
        ("k1", d[0, 0], oikea.k1, 0.02), ("k2", d[0, 1], oikea.k2, 0.1)):
    print(f"  {nimi}: arvio {arvio:7.{2 if raja < 1 else 0}f},"
          f" oikea {tosi:7.{2 if raja < 1 else 0}f},"
          f" virhe alle {raja:g}: {abs(arvio - tosi) < raja}")
# @loppu kalibrointi

# @alku pnp
# Kun kamera tunnetaan, yhdestä kuvasta saadaan laudan asento.
rvec, tvec = asennot()[3]
kuva = renderoi(oikea, lauta, rvec, tvec)
loytyi, kulmat = cv2.findChessboardCorners(kuva, kuvio)
kulmat = cv2.cornerSubPix(kuva, kulmat, (7, 7), (-1, -1), ehto)
onnistui, r_arvio, t_arvio = cv2.solvePnP(
    lauta.kulmat(), kulmat.astype(np.float64), oikea.K(),
    oikea.vaaristyma())
kulmavirhe = np.degrees(np.linalg.norm(r_arvio - rvec))
print(f"solvePnP: etäisyys {float(t_arvio[2, 0]):5.0f} mm"
      f" (oikea {float(tvec[2, 0]):5.0f} mm),"
      f" kiertovirhe alle 0,1 astetta {kulmavirhe < 0.1}")
# @loppu pnp
