"""Geometrinen jakauma: yrityksiä ensimmäiseen onnistumiseen."""

import numpy as np

# @alku teoria
p = 0.3                    # yksi yritys onnistuu 30 %:n todennäköisyydellä
print(f"odotettu yritysmäärä 1/p = {1 / p:.3f}")
for k in (1, 3, 5, 10):
    # P(tarvitaan yli k yritystä) = kaikki k ensimmäistä epäonnistuvat.
    print(f"P(yli {k:2} yritystä) = (1 - p)^{k} = {(1 - p) ** k:.4f}")
# @loppu teoria

# @alku simulointi
rng = np.random.default_rng(5)
yritykset = rng.geometric(p, size=200_000)
print(f"simulointi: keskiarvo {float(yritykset.mean()):.3f},"
      f" P(yli 10) = {float(np.mean(yritykset > 10)):.4f}")
# @loppu simulointi

# @alku muistiton
# Muistittomuus: jos 5 yritystä on jo epäonnistunut, jäljellä olevien
# yritysten jakauma on sama kuin alussa.
jatko = yritykset[yritykset > 5] - 5
print(f"5 epäonnistumisen jälkeen: keskiarvo {float(jatko.mean()):.3f}")
# @loppu muistiton
