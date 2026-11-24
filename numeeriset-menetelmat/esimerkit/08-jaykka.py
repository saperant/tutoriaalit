"""Jäykkä yhtälö: van der Polin oskillaattori, mu = 100."""

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp

MU = 100.0


# @alku malli
def vdp(t: float, y: npt.NDArray[np.float64]) -> list[float]:
    """y'' - mu (1 - y^2) y' + y = 0 ensimmäisen kertaluvun ryhmänä."""
    return [float(y[1]), float(MU * (1 - y[0] ** 2) * y[1] - y[0])]
# @loppu malli


# @alku vertailu
tulokset = {}
for menetelma in ("RK45", "Radau", "BDF"):
    r = solve_ivp(vdp, (0.0, 200.0), [2.0, 0.0], method=menetelma,
                  rtol=1e-6, atol=1e-8)
    tulokset[menetelma] = r
    print(f"{menetelma:5s} y(200) = {r.y[0, -1]:.4f}, onnistui: {r.success}")
rk, radau = tulokset["RK45"], tulokset["Radau"]
print(f"RK45 tarvitsi yli 10 kertaa enemmän funktion arvoja kuin Radau: "
      f"{rk.nfev > 10 * radau.nfev}")
print(f"RK45:n askelia yli 5000: {len(rk.t) > 5000}")
# @loppu vertailu
