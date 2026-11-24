"""2D-konvoluutio: filter2D, korrelaatio vs. konvoluutio ja reunat."""

import cv2
import numpy as np
import numpy.typing as npt

Kuva = npt.NDArray[np.float32]


# @alku oma
def konvoluutio(kuva: Kuva, ydin: Kuva) -> Kuva:
    """Suora 2D-konvoluutio, reunoilla peilaus (kuten BORDER_REFLECT_101)."""
    kh, kw = ydin.shape
    py, px = kh // 2, kw // 2
    laajennettu = np.pad(kuva, ((py, py), (px, px)), mode="reflect")
    kaannetty = ydin[::-1, ::-1]           # konvoluutio kääntää ytimen
    tulos = np.zeros_like(kuva)
    for dy in range(kh):
        for dx in range(kw):
            tulos += kaannetty[dy, dx] * laajennettu[
                dy:dy + kuva.shape[0], dx:dx + kuva.shape[1]]
    return tulos
# @loppu oma


# @alku vertailu
rng = np.random.default_rng(seed=3)
kuva = rng.uniform(0, 255, (40, 50)).astype(np.float32)
ydin = np.array([[1, 2, 0], [0, 1, -1], [0, 0, -2]], np.float32)

korrelaatio = cv2.filter2D(kuva, -1, ydin)           # ei käännä ydintä
kaannetty = cv2.flip(ydin, -1)
konv_opencv = cv2.filter2D(kuva, -1, kaannetty)
oma = konvoluutio(kuva, ydin)
print("filter2D on korrelaatio, ero omaan:",
      f"{float(np.abs(korrelaatio - oma).max()):.1f}")
ero = float(np.abs(konv_opencv - oma).max())
print("käännetyllä ytimellä sama kuin oma:", ero < 1e-3)
# @loppu vertailu

# @alku reunat
# Reunakäsittely ratkaisee, mitä kuvan ulkopuolella "on".
rivi = np.array([[10, 20, 30, 40]], np.float32)
keskiarvo = np.full((1, 3), 1 / 3, np.float32)
for nimi, tapa in (("REFLECT_101", cv2.BORDER_REFLECT_101),
                   ("REPLICATE", cv2.BORDER_REPLICATE),
                   ("CONSTANT 0", cv2.BORDER_CONSTANT)):
    tulos = cv2.filter2D(rivi, -1, keskiarvo, borderType=tapa)
    print(f"{nimi:12s}", " ".join(f"{v:6.2f}" for v in tulos[0]))
# @loppu reunat
