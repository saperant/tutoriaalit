"""Kuvaajan sudenkuopat: harva näytteistys ja asymptootit."""

import numpy as np

# @alku harva
# f(x) = sin(2 pi 99 x) värähtelee 99 kertaa välillä [0, 1].
for pisteita in [100, 101, 2000]:
    x = np.linspace(0.0, 1.0, pisteita)
    y = np.round(np.sin(2 * np.pi * 99 * x), 9)
    huiput = (y[1:-1] > 0.5) & (y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:])
    print(f"{pisteita:5d} pistettä: suurin |y| {np.max(np.abs(y)):.3f}, "
          f"näkyviä huippuja {np.count_nonzero(huiput)}")
# @loppu harva

# @alku asymptootti
x = np.linspace(0.0, np.pi, 1000)
y = np.tan(x)
hyppy = np.argmax(np.abs(np.diff(y)))
print(f"suurin hyppy x = {x[hyppy]:.4f} ... {x[hyppy + 1]:.4f}, "
      f"pi/2 = {np.pi / 2:.4f}")
print(f"arvot hypyn molemmin puolin: {y[hyppy]:.0f} ja {y[hyppy + 1]:.0f}")
# Viivan katkaisu: suuret arvot NaN:iksi, jolloin Matplotlib ei yhdistä.
katkaistu = np.where(np.abs(y) > 20, np.nan, y)
print("NaN-arvoja katkaisun jälkeen:", int(np.isnan(katkaistu).sum()))
# @loppu asymptootti
