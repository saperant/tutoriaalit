"""Syväoppivan mallin rajapinta: esikäsittely, IoU ja karsinta (NMS)."""

import cv2
import numpy as np

# @alku blob
# Verkon syöte on tyypillisesti NCHW-taulukko: kuvia x kanavat x korkeus x
# leveys, liukulukuina, normitettuna ja usein RGB-järjestyksessä.
kuva = np.zeros((480, 640, 3), np.uint8)
kuva[:, :, 2] = 200                                  # punainen (BGR)
blob = cv2.dnn.blobFromImage(kuva, scalefactor=1 / 255, size=(224, 224),
                             mean=(0, 0, 0), swapRB=True, crop=False)
print("blob:", blob.shape, blob.dtype)
print("kanavien keskiarvot:", " ".join(f"{v:.3f}" for v in
                                       blob[0].mean(axis=(1, 2))))
# @loppu blob


# @alku iou
def iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    """Leikkaus jaettuna yhdisteellä; laatikot muodossa (x, y, w, h)."""
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2 = min(a[0] + a[2], b[0] + b[2])
    y2 = min(a[1] + a[3], b[1] + b[3])
    leikkaus = max(0, x2 - x1) * max(0, y2 - y1)
    return leikkaus / (a[2] * a[3] + b[2] * b[3] - leikkaus)


# Malli antoi samasta kohteesta useita päällekkäisiä ehdokkaita.
ehdokkaat = [(100, 100, 80, 60), (104, 98, 82, 64), (96, 103, 78, 58),
             (300, 200, 50, 50), (305, 204, 48, 50)]
varmuudet = [0.91, 0.88, 0.70, 0.85, 0.40]
oikeat = [(102, 100, 80, 60), (302, 202, 50, 50)]
jaljella = cv2.dnn.NMSBoxes(ehdokkaat, varmuudet, score_threshold=0.5,
                            nms_threshold=0.5)
for i in sorted(int(j) for j in np.ravel(jaljella)):
    paras = max(iou(ehdokkaat[i], o) for o in oikeat)
    print(f"jäljelle jäi {ehdokkaat[i]}, varmuus {varmuudet[i]:.2f},"
          f" IoU oikeaan {paras:.2f}")
# @loppu iou
