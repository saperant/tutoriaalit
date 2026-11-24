"""Monte Carlo: piin arvio ja virheen pieneneminen kuten 1/sqrt(n)."""

import math

import numpy as np

# @alku pii
rng = np.random.default_rng(2718)
print("         n    arvio     virhe  virhe*sqrt(n)")
for k in range(2, 7):
    n = 10**k
    # Toistetaan 20 kertaa, jotta virheen suuruusluokka näkyy.
    arviot = [4 * float(np.mean((rng.random(n) ** 2
                                 + rng.random(n) ** 2) <= 1.0))
              for _ in range(20)]
    virhe = float(np.sqrt(np.mean((np.array(arviot) - math.pi) ** 2)))
    print(f"{n:>10,} {arviot[0]:8.4f} {virhe:9.5f}"
          f" {virhe * math.sqrt(n):8.2f}")
# @loppu pii
