"""Epästabiili ja stabiili rekursio samalle integraalijonolle.

I_n = integraali 0..1 x^n e^(x-1) dx toteuttaa I_n = 1 - n I_(n-1),
I_0 = 1 - 1/e. Kaikki I_n ovat välillä 0 < I_n < 1/(n+1).
"""

import math

from scipy import integrate


# @alku eteen
def eteenpain(n: int) -> list[float]:
    arvot = [1.0 - math.exp(-1.0)]
    for k in range(1, n + 1):
        arvot.append(1.0 - k * arvot[-1])  # virhe kertautuu k:lla
    return arvot
# @loppu eteen


# @alku taakse
def taaksepain(n: int, aloitus: int = 40) -> list[float]:
    """Aloitetaan arvauksella I_aloitus = 0; virhe jaetaan k:lla."""
    arvo = 0.0
    arvot = {aloitus: arvo}
    for k in range(aloitus, 0, -1):
        arvo = (1.0 - arvo) / k
        arvot[k - 1] = arvo
    return [arvot[k] for k in range(n + 1)]
# @loppu taakse


# @alku vertailu
eteen, taakse = eteenpain(20), taaksepain(20)
for n in (5, 10, 15, 17, 20):
    vertailu, _ = integrate.quad(lambda x, n: x**n * math.exp(x - 1),
                                 0, 1, args=(n,))
    print(f"n={n:2d}  eteenpäin {eteen[n]: .3e}   "
          f"taaksepäin {taakse[n]:.6f}   quad {vertailu:.6f}")
# I_0:n pyöristysvirhe on enintään eps/2 * I_0; se kertautuu 20!:lla.
virhe0 = 2.0**-53 * eteen[0]
print(f"I_0:n pyöristys <= {virhe0:.0e}, kertaa 20! = "
      f"{virhe0 * math.factorial(20):.0e}")
# @loppu vertailu
