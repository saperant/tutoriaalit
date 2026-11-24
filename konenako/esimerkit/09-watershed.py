"""Toisiinsa koskevien kappaleiden erottelu: etäisyysmuunnos ja watershed."""

import cv2
import numpy as np

# @alku kuva
# Kuusi kiekkoa, joista osa koskettaa toisiaan: kynnystys yhdistää ne.
maski = np.zeros((200, 300), np.uint8)
kiekot = [(60, 60), (105, 75), (200, 60), (80, 150), (190, 150), (235, 140)]
for keskipiste in kiekot:
    cv2.circle(maski, keskipiste, 30, 255, -1)
n_suora = cv2.connectedComponents(maski)[0] - 1
print(f"yhtenäisiä alueita {n_suora}, kiekkoja {len(kiekot)}")
# @loppu kuva

# @alku watershed
# 1. Etäisyys lähimpään taustapikseliin on suurin kiekkojen keskellä.
etaisyys = cv2.distanceTransform(maski, cv2.DIST_L2, 5)
# 2. Varmat keskustat: kaukana reunasta. Ne ovat siemenet.
_, keskustat = cv2.threshold(etaisyys, 0.75 * float(etaisyys.max()), 255,
                             cv2.THRESH_BINARY)
n_siemenet, siemenet = cv2.connectedComponents(keskustat.astype(np.uint8))
# 3. Varma tausta ja epävarma vyöhyke, jonka watershed jakaa.
varma_tausta = cv2.dilate(maski, np.ones((3, 3), np.uint8), iterations=3)
tuntematon = cv2.subtract(varma_tausta, keskustat.astype(np.uint8))
merkit = siemenet + 1                     # tausta 1, siemenet 2, 3, ...
merkit[tuntematon > 0] = 0                # 0 = watershed päättää
varikuva = cv2.cvtColor(maski, cv2.COLOR_GRAY2BGR)
tulos = cv2.watershed(varikuva, merkit)
alueet = [k for k in np.unique(tulos) if k > 1]
print(f"siemeniä {n_siemenet - 1}, watershed-alueita {len(alueet)}")
for k in alueet:
    ys, xs = np.nonzero(tulos == k)
    print(f"  alue keskellä ({xs.mean():5.1f}, {ys.mean():5.1f})")
# @loppu watershed
