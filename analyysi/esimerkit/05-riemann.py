"""Riemannin summat: integraali osavälien suorakulmioiden summana."""

import numpy as np
import numpy.typing as npt


def f(x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    return x**2


# @alku summat
def riemann(a: float, b: float, n: int, tapa: str) -> float:
    """Summa sum f(x_i) dx, kun x_i on osavälin vasen tai oikea
    päätepiste tai keskipiste."""
    dx = (b - a) / n
    vasemmat = a + dx * np.arange(n)
    siirto = {"vasen": 0.0, "oikea": 1.0, "keski": 0.5}[tapa]
    pisteet = np.asarray(vasemmat + siirto * dx, dtype=np.float64)
    return float(np.sum(f(pisteet)) * dx)


tarkka = 1 / 3                       # integraali x^2 välillä [0, 1]
print("     n   vasen virhe  oikea virhe  keski virhe")
for n in (10, 100, 1000):
    virheet = [riemann(0.0, 1.0, n, t) - tarkka
               for t in ("vasen", "oikea", "keski")]
    print(f"{n:6d}" + "".join(f"  {v:+.3e}" for v in virheet))
# @loppu summat
