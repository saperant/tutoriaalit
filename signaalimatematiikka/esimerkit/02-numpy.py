"""Kompleksiluvut NumPy-taulukoissa."""


import numpy as np


def kl(z: complex, d: int = 3) -> str:
    """Kompleksiluku pyöristettynä, ilman miinusnollia."""
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku numpy
zs = np.array([1 + 1j, -2 + 0j, 3j, 0.5 - 0.5j])
print("abs  :", np.round(np.abs(zs), 3))
print("kulma:", np.round(np.angle(zs, deg=True), 1) + 0.0)
print("conj :", ", ".join(kl(complex(c), 1) for c in np.conj(zs)))
yksikkö = np.exp(1j * np.angle(zs))       # pelkkä suunta
print("|e^(i kulma)|:", np.round(np.abs(yksikkö), 12))
print("dtype:", zs.dtype, "| reaaliosat:", zs.real)
# @loppu numpy
