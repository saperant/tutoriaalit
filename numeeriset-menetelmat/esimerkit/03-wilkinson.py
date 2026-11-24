"""Wilkinsonin polynomi: juuret ovat huonokuntoinen funktio kertoimista.

w(x) = (x - 1)(x - 2)...(x - 20). Kertoimet ovat kokonaislukuja, mutta
kertoimen x^19 pieni muutos siirtää juuria kauas.
"""

import numpy as np
from numpy.polynomial import polynomial as P

# @alku wilkinson
kertoimet = P.polyfromroots(np.arange(1, 21))[::-1]  # korkein aste ensin
print(f"x^19:n kerroin {kertoimet[1]:.0f}, "
      f"vakiotermi {kertoimet[-1]:.3e}")

hairitty = kertoimet.copy()
hairitty[1] -= 2.0**-23                 # suhteellinen muutos ~ 6e-10
juuret = np.sort_complex(np.roots(hairitty))
print("reaaliset:", " ".join(f"{z.real:.2f}" for z in juuret
                             if abs(z.imag) < 1e-6))
for z in juuret:
    if z.imag > 1e-6:                   # parit z ja sen liittoluku
        print(f"  {z.real:6.2f} +- {z.imag:.2f}i")
# @loppu wilkinson

# @alku herkkyys
# Ensimmäisen kertaluvun herkkyys: dr/da = -r^19 / w'(r). Juurelle 16
# muutos 2^-23 siirtää juurta yli kolmella yksiköllä.
for r in (5, 10, 16, 20):
    derivaatta = np.prod([r - k for k in range(1, 21) if k != r])
    print(f"juuri {r:2d}: |dr/da| = {abs(float(r) ** 19 / derivaatta):.1e}")
# @loppu herkkyys
