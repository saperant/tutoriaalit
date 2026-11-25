"""Korrelaatio ei ole syy-yhteys: yhteinen syy tuottaa korrelaation."""

import numpy as np

# @alku sekoittaja
# Palvelimen kuorma (pyyntöä/s) kasvattaa sekä muistinkäyttöä että
# vasteaikaa. Muisti ei vaikuta vasteaikaan lainkaan.
rng = np.random.default_rng(99)
n = 50_000
kuorma = rng.uniform(100.0, 1000.0, n)
muisti = 2.0 + 0.004 * kuorma + rng.normal(0.0, 0.4, n)      # Gt
vaste = 15.0 + 0.03 * kuorma + rng.normal(0.0, 3.0, n)       # ms
r = float(np.corrcoef(muisti, vaste)[0, 1])
print(f"muisti ja vasteaika, kaikki havainnot: r = {r:+.2f}")

# Kun kuorma pidetään lähes vakiona, yhteys katoaa.
for ala in (200.0, 500.0, 800.0):
    osa = (kuorma >= ala) & (kuorma < ala + 20.0)
    r_osa = float(np.corrcoef(muisti[osa], vaste[osa])[0, 1])
    print(f"kuorma {ala:.0f}-{ala + 20:.0f}: {int(osa.sum())} havaintoa,",
          f"r = {r_osa:+.2f}")
# @loppu sekoittaja
