"""Adaptiivinen askel: upotettu pari Heun (kertaluku 2) ja Euler (1)."""

from collections.abc import Callable

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp

Derivaatta = Callable[[float, float], float]


# @alku malli
# y' = -200 (t - 5) y^2, y(0) = 1/2501: ratkaisu y = 1 / (1 + 100 (t-5)^2)
# on terävä huippu kohdassa t = 5 ja muuten lähes vakio.
def f(t: float, y: float) -> float:
    return -200.0 * (t - 5.0) * y * y


def tarkka(t: float) -> float:
    return 1.0 / (1.0 + 100.0 * (t - 5.0) ** 2)
# @loppu malli


# @alku adaptiivinen
def heun_euler(f: Derivaatta, y: float, T: float,
               tol: float) -> tuple[float, list[float], list[float]]:
    """Kaksi ratkaisua samoista arvoista: niiden ero arvioi virheen.
    Askel hyväksytään, jos arvio <= tol, ja seuraava askel valitaan
    kaavalla h_uusi = 0.9 h sqrt(tol / arvio)."""
    t, h = 0.0, 0.01
    ajat, askeleet = [t], []
    while t < T:
        h = min(h, T - t)
        k1 = f(t, y)
        k2 = f(t + h, y + h * k1)
        euler = y + h * k1
        heun = y + h * (k1 + k2) / 2
        arvio = abs(heun - euler)
        if arvio <= tol:
            t, y = t + h, heun
            ajat.append(t)
            askeleet.append(h)
        h *= min(5.0, max(0.2, 0.9 * (tol / max(arvio, 1e-300)) ** 0.5))
    return y, ajat, askeleet
# @loppu adaptiivinen


# @alku vertailu
y, ajat, askeleet = heun_euler(f, tarkka(0.0), 10.0, 1e-6)
lyhin = min(range(len(askeleet)), key=askeleet.__getitem__)
print(f"askelia {len(askeleet)}, virhe hetkellä 10: "
      f"{abs(y - tarkka(10.0)):.0e}")
print(f"pisin askel {max(askeleet):.3f}, lyhin {askeleet[lyhin]:.1e} "
      f"hetkellä t = {ajat[lyhin]:.2f}")
def f_vektori(t: float, y: npt.NDArray[np.float64]) -> list[float]:
    return [f(t, float(y[0]))]


r = solve_ivp(f_vektori, (0.0, 10.0), [tarkka(0.0)], method="RK45",
              rtol=1e-8, atol=1e-10)
print(f"solve_ivp RK45: virhe < 1e-7: "
      f"{abs(r.y[0, -1] - tarkka(10.0)) < 1e-7}, askelia alle 500: "
      f"{len(r.t) < 500}")
# @loppu vertailu
