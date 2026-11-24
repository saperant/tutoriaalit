"""Riippumattomuus: rinnakkaiset palvelimet ja yhteinen vikasyy."""

import numpy as np

# @alku teoria
p_vika = 0.01          # yhden palvelimen todennäköisyys olla alhaalla
print(f"yksi palvelin: saatavuus {1 - p_vika:.4f}")
print(f"kaksi rinnakkain, riippumattomat: {1 - p_vika**2:.4f}")
print(f"kaksi sarjassa (molemmat tarvitaan): {(1 - p_vika)**2:.4f}")
# @loppu teoria

# @alku yhteinen
# Yhteinen vikasyy: sähkökatko (0,5 %) kaataa molemmat kerralla.
rng = np.random.default_rng(3)
n = 2_000_000
katko = rng.random(n) < 0.005
a_alhaalla = katko | (rng.random(n) < p_vika)
b_alhaalla = katko | (rng.random(n) < p_vika)
molemmat = float(np.mean(a_alhaalla & b_alhaalla))
erikseen = float(np.mean(a_alhaalla)) * float(np.mean(b_alhaalla))
print(f"P(A ja B alhaalla) = {molemmat:.5f},"
      f" P(A) P(B) = {erikseen:.5f}")
print(f"saatavuus yhteisellä vikasyyllä: {1 - molemmat:.4f}")
# @loppu yhteinen
