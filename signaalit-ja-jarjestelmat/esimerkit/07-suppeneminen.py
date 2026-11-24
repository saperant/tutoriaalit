"""Z-muunnoksen summa ja suppenemisalue: a^n u[n] <-> 1/(1 - a z^-1)."""

import numpy as np


# @alku suppeneminen
def osasumma(a: float, z: complex, N: int) -> complex:
    """sum_{n=0}^{N-1} a^n z^-n."""
    n = np.arange(N)
    return complex(np.sum((a / z) ** n))


a = 0.8
print(f"{'z':>6} {'|z|>a':>7} {'|S_50|':>10} {'|S_200|':>10}"
      f"   {'|1/(1-a/z)|':>8}")
for z in (2.0, 1.0, 0.9j, -0.85, 0.7, 0.5j):
    s50, s200 = osasumma(a, z, 50), osasumma(a, z, 200)
    kaava = 1 / (1 - a / z)
    print(f"{str(z):>6} {str(abs(z) > a):>7} {abs(s50):#10.4g}"
          f" {abs(s200):#10.4g}   {abs(kaava):8.4f}")
# @loppu suppeneminen
