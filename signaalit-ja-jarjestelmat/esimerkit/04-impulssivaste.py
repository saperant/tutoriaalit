"""LTI-järjestelmän tunnistus impulssivasteesta ja askelvasteesta."""

import numpy as np
import numpy.typing as npt

Jono = npt.NDArray[np.float64]


# @alku kaiku
def kaikuhuone(x: Jono) -> Jono:
    """Suora ääni ja kaksi heijastusta: viiveet 3 ja 7 näytettä."""
    y = x.copy()
    y[3:] += 0.5 * x[:-3]
    y[7:] -= 0.25 * x[:-7]
    return y
# @loppu kaiku


# @alku tunnistus
N = 20
d = np.zeros(N)
d[0] = 1.0
h = kaikuhuone(d)
print("h =", " ".join(f"{v:g}" for v in h[:9]))

askelvaste = kaikuhuone(np.ones(N))
print("askelvaste =", " ".join(f"{v:g}" for v in askelvaste[:9]))
print("askelvaste = cumsum(h):", bool(np.allclose(askelvaste, np.cumsum(h))))

x = np.array([1.0, 2.0, 0.0, -1.0] + [0.0] * (N - 4))
print("ennuste konvoluutiolla osuu:",
      bool(np.allclose(np.convolve(x, h)[:N], kaikuhuone(x))))
# @loppu tunnistus
