"""Kynnysilmaisu kohinassa: bittivirheen todennäköisyys Q-funktiolla."""

import math

import numpy as np


# @alku q
def q(x: float) -> float:
    """Normaalijakauman häntä P(Z > x) = erfc(x / sqrt(2)) / 2."""
    return 0.5 * math.erfc(x / math.sqrt(2))


# Bitti 0 lähetetään jännitteenä 0 V ja bitti 1 jännitteenä 1 V.
# Vastaanotin vertaa näytettä kynnykseen 0,5 V. Virhe syntyy, kun
# kohina vie näytteen kynnyksen väärälle puolelle: P = Q(d / (2 sigma)).
rng = np.random.default_rng(404)
d, n = 1.0, 2_000_000
bitit = rng.integers(0, 2, n)
for sigma in (0.5, 0.25, 0.15):
    naytteet = bitit * d + rng.normal(0.0, sigma, n)
    virheita = int(np.sum((naytteet > d / 2) != (bitit == 1)))
    print(f"sigma {sigma:.2f} V: teoria {q(d / (2 * sigma)):.5f},",
          f"simulointi {virheita / n:.5f}")
# @loppu q

# @alku valkoinen
# Valkoisen kohinan peräkkäiset näytteet ovat riippumattomia: näytteen
# ja sitä seuraavan näytteen korrelaatio on nolla. Liukuva keskiarvo
# tekee kohinasta värillistä: naapurinäytteet korreloivat.
kohina = rng.normal(0.0, 1.0, 200_000)
suodatettu = np.convolve(kohina, np.ones(4) / 4, mode="valid")
for nimi, x in (("valkoinen", kohina), ("suodatettu", suodatettu)):
    r = float(np.corrcoef(x[:-1], x[1:])[0, 1])
    print(f"{nimi}: peräkkäisten näytteiden korrelaatio",
          f"{round(r, 2) + 0.0:+.2f}")
# @loppu valkoinen
