"""Tuntemattoman jarjestelman tunnistus LMS- ja NLMS-suotimella."""

import numpy as np
from scipy import signal


# @alku nlms
def nlms(x: np.ndarray, d: np.ndarray, lkm: int, mu: float,
         normita: bool) -> tuple[np.ndarray, np.ndarray]:
    """Palauttaa painot jokaisen naytteen jalkeen ja virhesignaalin."""
    w = np.zeros(lkm)
    v = np.zeros(lkm)                       # viivelinja, v[0] uusin
    historia = np.zeros((x.size, lkm))
    e = np.zeros(x.size)
    for n in range(x.size):
        v = np.roll(v, 1)
        v[0] = x[n]
        e[n] = d[n] - w @ v                 # a priori -virhe
        askel = mu / (1e-8 + v @ v) if normita else mu
        w = w + askel * e[n] * v            # gradientin estimaatti e * v
        historia[n] = w
    return historia, e
# @loppu nlms


# @alku koe
rng = np.random.default_rng(2)
tuntematon = signal.firwin(8, 0.3)          # "kaiku" jota tunnistetaan
x = rng.standard_normal(5_000)
d = signal.lfilter(tuntematon, [1.0], x) + 0.01 * rng.standard_normal(x.size)
print("naytteita   LMS mu=0,02   NLMS mu=0,5   (virhe painoissa, dB)")
tulokset = [nlms(x, d, 8, 0.02, False)[0], nlms(x, d, 8, 0.5, True)[0]]
for n in (100, 500, 1_000, 5_000):
    rivi = [10 * np.log10(np.sum((w[n - 1] - tuntematon) ** 2)
                          / np.sum(tuntematon**2)) for w in tulokset]
    print(f"{n:8d} {rivi[0]:12.1f} {rivi[1]:13.1f}")
# @loppu koe
