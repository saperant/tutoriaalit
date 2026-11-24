"""Kalman-suodin seurannassa: tasainen nopeus, kohinaiset havainnot."""

import cv2
import numpy as np

# @alku malli
# Tila (x, y, vx, vy), havainto (x, y). Aika-askel on yksi kuva.
kf = cv2.KalmanFilter(4, 2)
kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                [0, 1, 0, 1],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]], np.float32)
kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
kf.processNoiseCov = np.diag([0.01, 0.01, 0.01, 0.01]).astype(np.float32)
kf.measurementNoiseCov = np.diag([16.0, 16.0]).astype(np.float32)  # 4 px
kf.errorCovPost = np.diag([100.0, 100.0, 10.0, 10.0]).astype(np.float32)
kf.statePost = np.array([[20], [50], [0], [0]], np.float32)
# @loppu malli

# @alku seuranta
rng = np.random.default_rng(seed=29)
oikea = np.array([20.0, 50.0])
nopeus = np.array([3.0, 1.5])
havaintovirheet, suodinvirheet = [], []
for kuva in range(100):
    oikea = oikea + nopeus
    havainto = oikea + rng.normal(0, 4.0, 2)
    if 40 <= kuva < 50:                  # kohde peittyy 10 kuvan ajaksi
        ennuste = kf.predict()
        kf.statePost = ennuste            # ei havaintoa: ennuste jää voimaan
        kf.errorCovPost = kf.errorCovPre
        arvio = ennuste[:2, 0]
    else:
        kf.predict()
        arvio = kf.correct(havainto.astype(np.float32).reshape(2, 1))[:2, 0]
        havaintovirheet.append(float(np.linalg.norm(havainto - oikea)))
    if kuva >= 10:                        # alun asettumisvaihe pois
        suodinvirheet.append(float(np.linalg.norm(arvio - oikea)))
    if kuva == 49:
        print(f"peiton lopussa ennusteen virhe alle 5 px:"
              f" {float(np.linalg.norm(arvio - oikea)) < 5}")
print(f"havaintojen keskivirhe {np.mean(havaintovirheet):4.1f} px")
print(f"suotimen keskivirhe   {np.mean(suodinvirheet):4.1f} px")
print("nopeusarvio:", " ".join(f"{v:3.1f}" for v in kf.statePost[2:, 0]),
      "(oikea 3.0 1.5)")
# @loppu seuranta
