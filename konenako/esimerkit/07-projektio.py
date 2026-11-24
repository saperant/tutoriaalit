"""Neulanreikäkamera: projektio käsin ja projectPoints-funktiolla."""

import cv2
import numpy as np

# @alku kasin
# Sisäiset parametrit: polttoväli pikseleinä ja pääpiste.
K = np.array([[800.0, 0.0, 320.0],
              [0.0, 800.0, 240.0],
              [0.0, 0.0, 1.0]])
# Ulkoiset parametrit: kamera on kiertynyt 10 astetta y-akselin ympäri
# ja maailman origo on 2 m kameran edessä.
rvec = np.array([0.0, np.radians(10.0), 0.0])
tvec = np.array([0.0, 0.0, 2000.0])
R, _ = cv2.Rodrigues(rvec)
X = np.array([[0.0, 0.0, 0.0], [300.0, -200.0, 100.0]])   # mm

kamerassa = X @ R.T + tvec                 # maailma -> kamera
homogeeninen = kamerassa @ K.T             # kamera -> kuva (homogeeninen)
pikselit = homogeeninen[:, :2] / homogeeninen[:, 2:]
for p, q in zip(X, pikselit, strict=True):
    print(f"{p.tolist()} mm -> ({q[0]:6.1f}, {q[1]:6.1f}) px")
# @loppu kasin

# @alku opencv
valmis, _ = cv2.projectPoints(X, rvec, tvec, K, None)
print("projectPoints sama:", bool(np.allclose(valmis.reshape(-1, 2),
                                              pikselit)))
# Mittakaava katoaa: kaksi kertaa suurempi maailma kaksi kertaa kauempana
# näyttää täsmälleen samalta.
tuplattu, _ = cv2.projectPoints(2 * X, rvec, 2 * tvec, K, None)
print("2 x koko ja 2 x etäisyys sama kuva:",
      bool(np.allclose(tuplattu, valmis)))
# @loppu opencv

# @alku vaaristyma
# Säteittäinen vääristymä siirtää pisteitä sitä enemmän, mitä
# kauempana ne ovat kuvan keskeltä (k1 < 0: tynnyrivääristymä).
d = np.array([-0.25, 0.08, 0.0, 0.0, 0.0])
reunat = np.array([[0.0, 0.0, 1.0], [0.1, 0.0, 1.0], [0.4, 0.3, 1.0]])
ideaali, _ = cv2.projectPoints(reunat, np.zeros(3), np.zeros(3), K, None)
vaaristynyt, _ = cv2.projectPoints(reunat, np.zeros(3), np.zeros(3), K, d)
for a, b in zip(ideaali.reshape(-1, 2), vaaristynyt.reshape(-1, 2),
                strict=True):
    print(f"ideaali ({a[0]:5.1f}, {a[1]:5.1f}) -> vääristynyt"
          f" ({b[0]:5.1f}, {b[1]:5.1f}), siirtymä"
          f" {float(np.linalg.norm(a - b)):4.1f} px")
# @loppu vaaristyma
