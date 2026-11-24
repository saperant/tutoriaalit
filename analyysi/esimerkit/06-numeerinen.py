"""Numeerinen integrointi: puolisuunnikas, Simpson ja quad."""

import math

import numpy as np
from scipy import integrate


# @alku saannot
def puolisuunnikas(y: np.ndarray, h: float) -> float:
    """Suorien paloilla: h (y0/2 + y1 + ... + y_{n-1} + yn/2)."""
    return float(h * (y[0] / 2 + np.sum(y[1:-1]) + y[-1] / 2))


def simpson(y: np.ndarray, h: float) -> float:
    """Paraabelin paloilla, osavälejä parillinen määrä:
    h/3 (y0 + 4 y1 + 2 y2 + 4 y3 + ... + yn)."""
    return float(h / 3 * (y[0] + 4 * np.sum(y[1:-1:2])
                          + 2 * np.sum(y[2:-1:2]) + y[-1]))
# @loppu saannot


# @alku vertailu
print("  n  puolisuunnikas  Simpson")
for n in (4, 8, 16, 32):
    x = np.linspace(0.0, math.pi, n + 1)
    h = math.pi / n
    y = np.sin(x)
    print(f"{n:3d}  {puolisuunnikas(y, h) - 2:+.3e}      "
          f"{simpson(y, h) - 2:+.3e}")
# Kun n kaksinkertaistuu, virhe pienenee 4- ja 16-kertaiseksi.
# @loppu vertailu

# @alku kirjasto
x = np.linspace(0.0, math.pi, 33)
print(f"scipy trapezoid {integrate.trapezoid(np.sin(x), x=x):.10f}")
print(f"scipy simpson   {integrate.simpson(np.sin(x), x=x):.10f}")
arvo, arvio = integrate.quad(math.sin, 0, math.pi)
print(f"scipy quad      {arvo:.10f} (virhearvio {arvio:.0e})")
# @loppu kirjasto
