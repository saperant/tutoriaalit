"""Butterworth vai Bessel: ylitys askelvasteessa."""

import math

from spice import lopeta, simuloi, vertaa


# @alku ylitys
def ylitys(Q: float) -> float:
    """Toisen kertaluvun alipäästön askelvasteen ylitys:
    vaimennus zeta = 1 / (2 Q), ylitys exp(-pi zeta / sqrt(1 - zeta^2))."""
    zeta = 1 / (2 * Q)
    return math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))
# @loppu ylitys


tulos = simuloi("04-bessel.cir").arvot
vertaa("Butterworth", tulos["huippu_b"] - 1, ylitys(1 / math.sqrt(2)), "",
       0.03)
vertaa("Bessel", tulos["huippu_s"] - 1, ylitys(1 / math.sqrt(3)), "", 0.1)
print(f"nousuaika 10-90 %: Butterworth {tulos['t_b'] * 1e6:.0f} us, "
      f"Bessel {tulos['t_s'] * 1e6:.0f} us")
lopeta()
