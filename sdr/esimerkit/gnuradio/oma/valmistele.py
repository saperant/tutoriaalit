"""Tekee vertailun lahtotiedot tutoriaalin omalla koodilla: tallenteen
asema.cu8 ja viitevastaanottimen aanen viite.f32.

Ajetaan tavallisella python3:lla (NumPy 2, SciPy), ei GNU Radiolla.
"""

import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "fm"))
import lahetin  # noqa: E402
import vastaanotin as va  # noqa: E402

Reaali = NDArray[np.float64]


# @alku viite
def mono(z: va.Kompleksi) -> tuple[Reaali, float]:
    """Luvun 5 monoketju: kanava, ilmaisin, 15 kHz:n alipaasto,
    48 kHz ja jalkikorostus. Palauttaa aanen ja kanavan tason (dBFS)."""
    kanava = va.valitse_kanava(z, lahetin.FS_IQ, 200e3, 4)
    m = va.fm_ilmaisin(kanava, lahetin.FS_MPX, lahetin.POIKKEAMA)
    h = signal.firwin(255, 15_000.0, fs=lahetin.FS_MPX)
    summa = signal.lfilter(h, [1.0], m)
    aani = signal.resample_poly(summa, 4, 19)
    b, a = va.jalkikorostus(va.FS_AANI)
    tulos: Reaali = signal.lfilter(b, a, aani)
    taso = 10 * np.log10(float(np.mean(np.abs(kanava) ** 2)))
    return tulos, taso
# @loppu viite


if __name__ == "__main__":
    rng = np.random.default_rng(2026)
    z = lahetin.tallenne(kesto=1.2, cnr_db=35.0, rng=rng)
    lahetin.kirjoita_cu8(Path("asema.cu8"), z, taysi=4 * np.std(z))
    aani, taso = mono(va.lue_cu8(Path("asema.cu8")))
    aani.astype("<f4").tofile("viite.f32")
    Path("viite-taso.txt").write_text(f"{taso:.2f}\n", encoding="utf-8")
