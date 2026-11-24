"""Monte Carlo -tuloksen luotettavuus: virheiden määrä ja luottamusväli."""

import numpy as np
from scipy.stats import binomtest


# @alku vali
def wilson(virheita: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilsonin 95 %:n luottamusväli virhetodennäköisyydelle."""
    p = virheita / n
    keski = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    leveys = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return keski - leveys, keski + leveys


print("virheitä   bittejä      BER     95 %:n väli          suhteellinen")
for virheita, n in ((1, 100_000), (10, 1_000_000), (100, 10_000_000),
                    (1_000, 100_000_000)):
    ala, yla = wilson(virheita, n)
    suhteellinen = 50 * (yla - ala) / (virheita / n)
    print(f"{virheita:8d}  {n:9d}  {virheita / n:.1e}"
          f"  {ala:.2e} ... {yla:.2e}   +-{suhteellinen:4.0f} %")
# @loppu vali

# @alku nolla
# Nolla virhettä ei todista, että BER = 0: 95 %:n yläraja on noin 3 / n.
n = 1_000_000
yla = binomtest(0, n, 1e-6, alternative="less").proportion_ci(0.95).high
print(f"0 virhettä {n} bitissä: BER < {yla:.1e} (95 %)")
# @loppu nolla
