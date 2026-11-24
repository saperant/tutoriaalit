"""Newtonin menetelmä epälineaariselle yhtälöryhmälle F(x) = 0."""

import numpy as np
import numpy.typing as npt
from scipy import optimize

Vektori = npt.NDArray[np.float64]


# @alku malli
# Ympyrän x^2 + y^2 = 4 ja käyrän y = e^x - 1 leikkauspiste.
def F(v: Vektori) -> Vektori:
    x, y = v
    return np.array([x * x + y * y - 4.0, np.exp(x) - 1.0 - y])


def J(v: Vektori) -> Vektori:
    """Jacobin matriisi: osittaisderivaatat dF_i / dx_j."""
    x, y = v
    return np.array([[2 * x, 2 * y], [np.exp(x), -1.0]])
# @loppu malli


# @alku newton
x = np.array([1.0, 1.0])
for k in range(5):
    # Ratkaistaan J dx = -F; käänteismatriisia ei muodosteta.
    dx = np.linalg.solve(J(x), -F(x))
    x = x + dx
    jaannos = np.linalg.norm(F(x))
    teksti = f"{jaannos:.1e}" if jaannos > 1e-14 else "< 1e-14"
    print(f"k={k + 1}  x=({x[0]:.10f}, {x[1]:.10f})  |F| {teksti}")
# @loppu newton

# @alku scipy
ratkaisu = optimize.root(F, [1.0, 1.0], jac=J, method="hybr")
print(f"optimize.root: ({ratkaisu.x[0]:.10f}, {ratkaisu.x[1]:.10f}), "
      f"onnistui: {ratkaisu.success}")
# @loppu scipy
