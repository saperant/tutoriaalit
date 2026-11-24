"""Sovellus: liikkuvan pallon ja kiinteän tolpan törmäyshetki."""

import math

import numpy as np
import numpy.typing as npt

Vektori = npt.NDArray[np.float64]


# @alku tormays
def tormayshetki(p0: Vektori, v: Vektori, keskus: Vektori,
                 r: float) -> float | None:
    """Pienin t >= 0, jolla |p0 + v t - keskus| = r, tai None.

    Ehto on toisen asteen yhtälö a t^2 + b t + c = 0, jossa
    a = v.v, b = 2 (p0 - keskus).v ja c = |p0 - keskus|^2 - r^2."""
    d = p0 - keskus
    a = float(v @ v)
    b = 2.0 * float(d @ v)
    c = float(d @ d) - r * r
    if c <= 0.0:
        return 0.0                       # jo kosketuksessa
    diskriminantti = b * b - 4.0 * a * c
    if a == 0.0 or diskriminantti < 0.0:
        return None                      # ei liiku tai ohittaa
    t = (-b - math.sqrt(diskriminantti)) / (2.0 * a)
    return t if t >= 0.0 else None
# @loppu tormays


# @alku kaytto
p0 = np.array([0.0, 0.0])
keskus = np.array([10.0, 1.0])
r = 1.5                                  # pallon ja tolpan säteet yhteensä
for vx, vy in [(5.0, 0.0), (5.0, 2.0), (-5.0, 0.0)]:
    t = tormayshetki(p0, np.array([vx, vy]), keskus, r)
    print(f"v = ({vx}, {vy}): ", "ei osu" if t is None else f"t = {t:.4f} s")
# @loppu kaytto

# @alku tunnelointi
# Kehyksittäinen tarkistus 30 kertaa sekunnissa ohittaa nopean pallon:
# se on kehyksessä 2 kohdassa x = 10 ja kehyksessä 3 kohdassa x = 15.
v = np.array([150.0, 0.0])
tolppa = np.array([12.0, 1.0])
osui = any(np.linalg.norm(p0 + v * k / 30 - tolppa) <= r
           for k in range(31))
print("kehystarkistus osui:", osui)
t = tormayshetki(p0, v, tolppa, r)
print("analyyttinen hetki:", "ei osu" if t is None else f"{t:.5f} s")
# @loppu tunnelointi
