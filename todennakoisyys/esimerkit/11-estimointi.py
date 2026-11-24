"""Estimointi: harhaton varianssi ja suurimman uskottavuuden menetelmä."""

import numpy as np

rng = np.random.default_rng(55)

# @alku harha
# Pienen otoksen (n = 5) varianssi jakajalla n on harhainen:
# odotusarvo on (n - 1)/n * sigma^2. Jakaja n - 1 korjaa harhan.
otokset = rng.normal(0.0, 2.0, size=(200_000, 5))      # sigma^2 = 4
print(f"jakaja n:     keskiarvo {float(otokset.var(axis=1).mean()):.3f}"
      f" (teoria {4 * 4 / 5:.3f})")
print(f"jakaja n - 1: keskiarvo"
      f" {float(otokset.var(axis=1, ddof=1).mean()):.3f} (teoria 4.000)")
# @loppu harha

# @alku ml
# Eksponenttijakauman suurimman uskottavuuden estimaatti on 1/keskiarvo.
# Esimerkki: komponenttien elinajat tunteina, todellinen vikataajuus
# 1/1000 h.
elinajat = rng.exponential(1000.0, size=50)
lam_hattu = 1 / float(elinajat.mean())
print(f"ML-estimaatti: lambda = {lam_hattu:.6f} /h"
      f" (MTBF {1 / lam_hattu:.0f} h, todellinen 1000 h)")
# Uskottavuusfunktio on suurimmillaan estimaatin kohdalla.
for lam in (0.5 * lam_hattu, lam_hattu, 1.5 * lam_hattu):
    logL = elinajat.size * np.log(lam) - lam * float(elinajat.sum())
    print(f"  lambda = {lam:.6f}: log L = {float(logL):.2f}")
# @loppu ml
