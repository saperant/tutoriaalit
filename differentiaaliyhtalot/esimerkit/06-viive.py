"""Viivästetty heräte: pulssi Heavisiden funktiolla ja Laplacella."""

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

t = sp.symbols("t", positive=True)
s = sp.symbols("s")

# @alku pulssi
# RC-tyyppinen järjestelmä y' + y = u(t), y(0) = 0. Tulo u on pulssi:
# kytketään päälle hetkellä 1 ja pois hetkellä 3. Heavisiden
# funktiolla u = H(t - 1) - H(t - 3), ja viivesäännöllä
# U(s) = (exp(-s) - exp(-3 s)) / s.
U = (sp.exp(-s) - sp.exp(-3 * s)) / s
Y = U / (s + 1)
y = sp.inverse_laplace_transform(Y, s, t)
# Ryhmitellään termit kytkentähetkittäin: kumpikin askel tuottaa oman
# ensimmäisen kertaluvun vasteensa omasta hetkestään alkaen.
ryhmat = sp.collect(
    sp.expand(y), [sp.Heaviside(t - 1), sp.Heaviside(t - 3)], evaluate=False
)
for askel, kerroin in sorted(
    ryhmat.items(), key=lambda p: str(p[0])
):
    print(f"{askel} * ({sp.powsimp(kerroin)})")
# @loppu pulssi

# @alku tarkistus
lauseke = sp.lambdify(t, y, "numpy")


def f(tt: float, z: np.ndarray) -> np.ndarray:
    u = 1.0 if 1.0 <= tt < 3.0 else 0.0
    return np.array([u - z[0]])


r = solve_ivp(
    f,
    (0, 6),
    [0.0],
    t_eval=[2.0, 3.0, 5.0],
    max_step=0.01,
    rtol=1e-9,
    atol=1e-12,
)
for tt, arvo in zip(r.t, r.y[0], strict=True):
    print(
        f"t = {tt:.0f}: Laplace {float(lauseke(tt)):.4f}, "
        f"solve_ivp {arvo:.4f}"
    )
# @loppu tarkistus
