"""Homografia: dokumentin oikaisu, DLT ja RANSAC väärien parien kanssa."""

import cv2
import numpy as np
import numpy.typing as npt

Pisteet = npt.NDArray[np.float64]

# @alku oikaisu
# Kuvattu A4-arkki näkyy vinosti. Neljästä kulmasta saadaan homografia,
# joka oikaisee arkin 210 x 297 pikselin kuvaksi (1 px = 1 mm).
kulmat_kuvassa = np.array([[112, 64], [371, 98], [402, 455], [58, 410]],
                          np.float32)
kulmat_arkilla = np.array([[0, 0], [210, 0], [210, 297], [0, 297]],
                          np.float32)
H = cv2.getPerspectiveTransform(kulmat_kuvassa, kulmat_arkilla)
keskikohta = cv2.perspectiveTransform(
    np.array([[[230.0, 255.0]]], np.float32), H)[0, 0]
print("kuvan piste (230, 255) on arkilla kohdassa",
      f"({keskikohta[0]:.1f}, {keskikohta[1]:.1f}) mm")
# @loppu oikaisu


# @alku dlt
def dlt(a: Pisteet, b: Pisteet) -> Pisteet:
    """Homografia vähintään neljästä parista: Ah = 0, ratkaisu SVD:llä."""
    rivit = []
    for (x, y), (u, v) in zip(a, b, strict=True):
        rivit.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        rivit.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    _, _, vt = np.linalg.svd(np.array(rivit))
    h = vt[-1].reshape(3, 3)                 # pienintä singulaariarvoa
    return np.asarray(h / h[2, 2], np.float64)  # vastaava sing.vektori


oma = dlt(kulmat_kuvassa.astype(np.float64),
          kulmat_arkilla.astype(np.float64))
print("oma DLT = getPerspectiveTransform:",
      bool(np.allclose(oma, H, atol=1e-6)))
# @loppu dlt

# @alku ransac
# 100 vastinparia tunnetulla homografialla, kohinaa 0,5 px ja 30 %
# täysin vääriä pareja. Pienimmän neliösumman ratkaisu kaikista pareista
# hajoaa, RANSAC löytää oikeat parit.
rng = np.random.default_rng(seed=6)
a = rng.uniform(0, 400, (100, 2))
b = cv2.perspectiveTransform(a[None].astype(np.float64), np.linalg.inv(H))[0]
b += rng.normal(0, 0.5, b.shape)
vaarat = np.zeros(100, bool)
vaarat[rng.choice(100, size=30, replace=False)] = True
b[vaarat] = rng.uniform(0, 400, (30, 2))
oikea = np.linalg.inv(H) / np.linalg.inv(H)[2, 2]


def virhe(arvio: np.ndarray) -> float:
    """Kulmapisteiden siirtymä arvion ja oikean välillä pikseleinä."""
    p = kulmat_arkilla[None].astype(np.float64)
    ero = cv2.perspectiveTransform(p, arvio) - cv2.perspectiveTransform(
        p, oikea)
    return float(np.linalg.norm(ero, axis=2).max())


kaikki, _ = cv2.findHomography(a, b, method=0)
cv2.setRNGSeed(1)
ransac, maski = cv2.findHomography(a, b, cv2.RANSAC, 3.0)
print(f"väärien osuus {100 * vaarat.mean():.0f} %")
print(f"pienin neliösumma: kulmavirhe yli 10 px {virhe(kaikki) > 10}")
hyvaksytyt_vaarat = int((maski.ravel() > 0)[vaarat].sum())
print(f"RANSAC: kulmavirhe alle 2 px {virhe(ransac) < 2},"
      f" oikeiksi luokitellut väärät {hyvaksytyt_vaarat}")
# @loppu ransac
