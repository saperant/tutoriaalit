"""Varianssin laskusäännöt: toleranssien kasautuminen."""

import math

import numpy as np

# @alku kasautuminen
# Kymmenen sarjaan kytkettyä vastusta, kukin 100 ohmia +-1 % (3 sigma).
n, nimellinen, toleranssi = 10, 100.0, 0.01
sigma = nimellinen * toleranssi / 3
pahin = n * nimellinen * toleranssi
tilastollinen = 3 * math.sqrt(n) * sigma     # varianssit summautuvat
print(f"pahimman tapauksen poikkeama: +-{pahin:.2f} ohmia")
print(f"tilastollinen (RSS, 3 sigma): +-{tilastollinen:.2f} ohmia")
# @loppu kasautuminen

# @alku simulointi
rng = np.random.default_rng(17)
vastukset = rng.normal(nimellinen, sigma, size=(500_000, n))
summa = vastukset.sum(axis=1)
poikkeama = np.abs(summa - n * nimellinen)
print(f"simulointi: keskihajonta {float(summa.std()):.3f}"
      f" (teoria {math.sqrt(n) * sigma:.3f})")
yli_rss = float(np.mean(poikkeama > tilastollinen))
print(f"poikkeama yli RSS-rajan: {yli_rss:.4f},"
      f" yli 5 ohmia: {float(np.mean(poikkeama > 5)):.6f}")
# @loppu simulointi

# @alku skaalaus
# Var(aX + b) = a^2 Var(X): yksikkömuunnos ei lisää epävarmuutta.
x = rng.normal(20.0, 0.5, 200_000)        # lämpötila celsiusasteina
f = 1.8 * x + 32                          # fahrenheitiksi
print(f"Var(C) = {float(x.var()):.4f}, Var(F) = {float(f.var()):.4f},"
      f" 1.8^2 Var(C) = {1.8**2 * float(x.var()):.4f}")
# @loppu skaalaus
