"""Epipolaarigeometria: essentiaalimatriisi ja kameran liike pisteistä."""

import cv2
import numpy as np

# @alku pisteet
rng = np.random.default_rng(seed=13)
K = np.array([[700.0, 0.0, 320.0], [0.0, 700.0, 240.0], [0.0, 0.0, 1.0]])
# 3D-pisteet kameran edessä 1,5-8 m etäisyydellä. Syvyyden vaihtelu
# erottaa kierron ja sivuttaissiirron toisistaan.
X = rng.uniform((-1500, -1000, 1500), (1500, 1000, 8000), (80, 3))
# Toinen kamera: kierto 5 astetta y-akselin ympäri ja siirto 0,5 m
# oikealle. Kamera 1 on origossa.
R_tosi, _ = cv2.Rodrigues(np.array([0.0, np.radians(5.0), 0.0]))
t_tosi = np.array([-500.0, 0.0, 0.0])          # X_2 = R X_1 + t
p1, _ = cv2.projectPoints(X, np.zeros(3), np.zeros(3), K, None)
p2, _ = cv2.projectPoints(X, cv2.Rodrigues(R_tosi)[0], t_tosi, K, None)
p1 = p1.reshape(-1, 2) + rng.normal(0, 0.3, (80, 2))   # mittauskohina
p2 = p2.reshape(-1, 2) + rng.normal(0, 0.3, (80, 2))
# @loppu pisteet

# @alku essentiaali
cv2.setRNGSeed(1)
E, maski = cv2.findEssentialMat(p1, p2, K, cv2.RANSAC, 0.999, 1.0)
hyvia, R, t, _ = cv2.recoverPose(E, p1, p2, K)
kiertovirhe = np.degrees(np.linalg.norm(cv2.Rodrigues(R @ R_tosi.T)[0]))
suunta = t.ravel() / np.linalg.norm(t)
print(f"kiertovirhe alle 0,5 astetta: {kiertovirhe < 0.5}")


def vektori(v: np.ndarray) -> str:
    # round(...) + 0.0 muuttaa luvun -0.0 nollaksi.
    return " ".join(f"{round(float(x), 2) + 0.0:5.2f}" for x in v)


print("siirron suunta (pituus 1):", vektori(suunta))
print("oikea suunta:            ", vektori(t_tosi / np.linalg.norm(t_tosi)))
# @loppu essentiaali

# @alku rajoite
# Epipolaarirajoite x2^T F x1 = 0: vastinpiste on epipolaarisuoralla.
F = np.linalg.inv(K).T @ E @ np.linalg.inv(K)
h1 = np.hstack([p1, np.ones((80, 1))])
h2 = np.hstack([p2, np.ones((80, 1))])
suorat = h1 @ F.T                                  # suorat kuvassa 2
etaisyys = np.abs(np.sum(suorat * h2, axis=1)) / np.hypot(
    suorat[:, 0], suorat[:, 1])
print(f"etäisyys epipolaarisuorasta: mediaani alle 1 px"
      f" {float(np.median(etaisyys)) < 1.0}")
# @loppu rajoite
