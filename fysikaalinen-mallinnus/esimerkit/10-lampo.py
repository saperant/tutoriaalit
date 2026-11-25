"""Levyn lämpeneminen ajan funktiona: M T' + K T = b implisiittisellä
Eulerilla ja energiatase joka askeleella.

Sama alumiinilevy kuin luvussa 7: osalämmitin vasemmalla, konvektio
oikealla. Levy on aluksi ilman lämpötilassa."""

import math
import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import splu

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import (  # noqa: E402
    jaykkyys,
    massa,
    reunakuorma,
    reunamatriisi,
    suorakulmio,
)

K, RHO_C, H = 200.0, 2.43e6, 50.0      # W/(m K), J/(m³ K), W/(m² K)
T_ILMA, VUO = 20.0, 5000.0
LEVEYS, KORKEUS = 0.100, 0.050
DT, ASKELIA = 60.0, 400

# @alku kokoaminen
verkko = suorakulmio(40, 20, LEVEYS, KORKEUS)
x, y = verkko.pisteet[:, 0], verkko.pisteet[:, 1]
sarmat = verkko.reunasarmat()
x0, x1 = x[sarmat[:, 0]], x[sarmat[:, 1]]
y0, y1 = y[sarmat[:, 0]], y[sarmat[:, 1]]
oikea = sarmat[(x0 > LEVEYS - 1e-9) & (x1 > LEVEYS - 1e-9)]
kolmannes = ((x0 < 1e-9) & (x1 < 1e-9)
             & (np.minimum(y0, y1) > KORKEUS / 3 - 1e-9)
             & (np.maximum(y0, y1) < 2 * KORKEUS / 3 + 1e-9))
lammitin = sarmat[kolmannes]

m = RHO_C * massa(verkko)
hm = reunamatriisi(verkko, oikea, H)
a = jaykkyys(verkko, K) + hm
b = reunakuorma(verkko, lammitin, VUO) + hm @ np.full(len(x), T_ILMA)
# @loppu kokoaminen

# @alku aika
# Implisiittinen Euler: (M + dt A) T_uusi = M T_vanha + dt b.
# Matriisi ei muutu, joten se hajotetaan kerran.
hajotelma = splu((m + DT * a).tocsc())
t = np.full(len(x), T_ILMA)
teho_sisaan = float(np.sum(reunakuorma(verkko, lammitin, VUO)))
tuotu = poistunut = 0.0
aikavakio = RHO_C * LEVEYS * KORKEUS / (H * KORKEUS)   # yksi lämpötila
print(f"yhden lämpötilan mallin aikavakio: {aikavakio:.0f} s")
print("  aika s  keski °C  yksi lämpötila °C  kuumin °C  taseen virhe")
for askel in range(1, ASKELIA + 1):
    t = hajotelma.solve(m @ t + DT * b)
    tuotu += DT * teho_sisaan
    poistunut += DT * float(np.sum(hm @ (t - T_ILMA)))
    if askel % 80 == 0:
        varasto = float(np.sum(m @ (t - T_ILMA)))
        keski = T_ILMA + varasto / (RHO_C * LEVEYS * KORKEUS)
        aika = askel * DT
        malli = T_ILMA + teho_sisaan / (H * KORKEUS) * (
            1.0 - math.exp(-aika / aikavakio))
        virhe = abs(tuotu - poistunut - varasto) / tuotu
        print(f"{aika:8.0f} {keski:9.2f} {malli:18.2f} {t.max():10.2f}  "
              + ("alle 1e-9" if virhe < 1e-9 else f"{virhe:.1e}"))
# @loppu aika
