"""Kynnystys: kiinteä, Otsu ja adaptiivinen epätasaisessa valaistuksessa."""

import cv2
import numpy as np

# @alku kuva
# Tummaa tekstiä vaalealla paperilla. Valaistus heikkenee oikealle,
# joten oikean reunan paperi on tummempi kuin vasemman reunan teksti.
rng = np.random.default_rng(seed=11)
oikea = np.zeros((120, 400), np.uint8)              # tunnettu totuus
for i, sana in enumerate(("KYNNYS", "VALO")):
    cv2.putText(oikea, sana, (10 + 200 * i, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, 255, thickness=4)
paperi = np.where(oikea > 0, 60.0, 200.0)
valaistus = np.linspace(1.0, 0.25, 400)[None, :]
kuva = paperi * valaistus + rng.normal(0, 4, paperi.shape)
kuva = np.clip(kuva, 0, 255).astype(np.uint8)
teksti = oikea > 0
# @loppu kuva


# @alku vertailu
def virhe(maski: np.ndarray) -> float:
    """Väärin luokiteltujen pikselien osuus (teksti = 255)."""
    return float(np.mean((maski > 0) != teksti))


_, kiintea = cv2.threshold(kuva, 100, 255, cv2.THRESH_BINARY_INV)
t, otsu = cv2.threshold(kuva, 0, 255,
                        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
adaptiivinen = cv2.adaptiveThreshold(
    kuva, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
    blockSize=31, C=10)
print(f"kiinteä 100:  virhe {100 * virhe(kiintea):5.1f} %")
print(f"Otsu ({t:3.0f}):   virhe {100 * virhe(otsu):5.1f} %")
print(f"adaptiivinen: virhe {100 * virhe(adaptiivinen):5.1f} %")
# @loppu vertailu
