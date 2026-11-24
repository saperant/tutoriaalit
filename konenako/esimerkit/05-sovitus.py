"""Piirteiden sovittaminen: ORB ja SIFT, ratio-testi ja tunnettu muunnos."""

import cv2
import numpy as np

# @alku kuvat
# Teksturoitu näkymä satunnaisista kuvioista ja sen kierretty, pienennetty
# ja siirretty versio. Muunnos tunnetaan, joten vastinparit voi tarkistaa.
rng = np.random.default_rng(seed=12)
nakyma: np.ndarray = np.full((300, 400), 120, np.uint8)
for _ in range(60):
    x, y = (int(v) for v in rng.integers((0, 0), (400, 300)))
    savy = int(rng.integers(0, 256))
    if rng.random() < 0.5:
        cv2.circle(nakyma, (x, y), int(rng.integers(5, 25)), savy, -1)
    else:
        w, h = (int(v) for v in rng.integers(10, 40, size=2))
        cv2.rectangle(nakyma, (x, y), (x + w, y + h), savy, -1)
nakyma = cv2.GaussianBlur(nakyma, (3, 3), 0)
muunnos = cv2.getRotationMatrix2D((200, 150), angle=25, scale=0.8)
muunnos[:, 2] += (15, -10)
toinen = cv2.warpAffine(nakyma, muunnos, (400, 300), borderValue=120)
# @loppu kuvat


# @alku sovitus
def sovita(nimi: str, ilmaisin: cv2.Feature2D, normi: int) -> None:
    kp1, d1 = ilmaisin.detectAndCompute(nakyma, None)
    kp2, d2 = ilmaisin.detectAndCompute(toinen, None)
    parit = cv2.BFMatcher(normi).knnMatch(d1, d2, k=2)
    # Loween ratio-testi: paras vastine selvästi parempi kuin toiseksi
    # paras, muuten piste on monitulkintainen.
    hyvat = [p[0] for p in parit
             if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
    a = np.array([kp1[m.queryIdx].pt for m in hyvat], np.float32)
    b = np.array([kp2[m.trainIdx].pt for m in hyvat], np.float32)
    odotettu = a @ muunnos[:, :2].T + muunnos[:, 2]
    oikein = np.linalg.norm(b - odotettu, axis=1) < 3.0
    print(f"{nimi}: piirteitä yli 100 {min(len(kp1), len(kp2)) > 100},"
          f" pareja yli 50 {len(hyvat) > 50},"
          f" oikeita yli 80 % {oikein.mean() > 0.8}")
    arvio, _ = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC)
    kulma = np.degrees(np.arctan2(arvio[1, 0], arvio[0, 0]))
    skaala = float(np.hypot(arvio[0, 0], arvio[1, 0]))
    print(f"  RANSAC-arvio: kierto {-kulma:.1f} astetta, skaala {skaala:.2f}")


cv2.setRNGSeed(1)
sovita("ORB", cv2.ORB.create(nfeatures=1000), cv2.NORM_HAMMING)
sovita("SIFT", cv2.SIFT.create(), cv2.NORM_L2)
# @loppu sovitus
