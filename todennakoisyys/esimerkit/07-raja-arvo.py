"""Keskeinen raja-arvolause: summat lähestyvät normaalijakaumaa."""

import math

import numpy as np
import numpy.typing as npt


# @alku histogrammi
def histogrammi(x: npt.NDArray[np.float64], alku: float, loppu: float,
                lokeroita: int = 9, leveys: int = 40) -> None:
    """Tulostaa tekstihistogrammin."""
    maarat, reunat = np.histogram(x, bins=lokeroita, range=(alku, loppu))
    suurin = int(maarat.max())
    for m, a in zip(maarat, reunat, strict=False):
        palkki = "#" * round(leveys * int(m) / suurin)
        print(f"{float(a):6.2f} {palkki}".rstrip())
# @loppu histogrammi


# @alku summat
rng = np.random.default_rng(8)
for n in (1, 2, 12):
    # n tasajakautuneen luvun summa, keskitettynä ja skaalattuna.
    s = rng.random((200_000, n)).sum(axis=1)
    z = (s - n / 2) / math.sqrt(n / 12)
    print(f"n = {n}: P(|Z| < 1) = {float(np.mean(np.abs(z) < 1)):.3f}"
          f" (normaali 0.683)")
    if n in (1, 12):
        histogrammi(z, -3.0, 3.0)
# @loppu summat

# @alku vino
# Vino jakauma tarvitsee enemmän termejä: eksponenttijakauman summa.
for n in (1, 5, 50):
    s = rng.exponential(1.0, (200_000, n)).sum(axis=1)
    z = (s - n) / math.sqrt(n)
    vinous = float(np.mean(z**3))
    print(f"Exp-summa n = {n:2}: vinous {vinous:.3f}"
          f" (teoria {2 / math.sqrt(n):.3f}, normaali 0)")
# @loppu vino
