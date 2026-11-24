"""Geometrinen summa ja Dirichlet'n ydin."""


import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku geometrinen
def geometrinen(r: complex, n: int) -> complex:
    """Summa r^0 + r^1 + ... + r^(n-1) suljetussa muodossa."""
    if r == 1:
        return complex(n)
    return (1 - r**n) / (1 - r)


for r in [0.5 + 0j, -0.9 + 0j, 0.6j, np.exp(0.4j)]:
    suora = sum(complex(r) ** k for k in range(20))
    print(f"r = {kl(complex(r), 2):>14}: silmukka {kl(suora)},"
          f" kaava {kl(geometrinen(complex(r), 20))}")
print(f"0.5:n äärettömän sarjan summa 1/(1 - r) = {1 / (1 - 0.5):.1f},"
      f" 60 termiä: {geometrinen(0.5, 60).real:.15f}")
# @loppu geometrinen


# @alku dirichlet
def dirichlet(x: Taulukko, N: int) -> Taulukko:
    """sum_{k=-N}^{N} e^(ikx) = sin((N + 1/2) x) / sin(x / 2)."""
    return np.sin((N + 0.5) * x) / np.sin(x / 2)


x = np.linspace(0.01, np.pi, 500)
N = 6
k = np.arange(-N, N + 1)[:, np.newaxis]           # sarakkeena
suora_d = np.sum(np.exp(1j * k * x), axis=0)       # summa rivien yli
print("Dirichlet'n ydin = summa:",
      bool(np.allclose(suora_d, dirichlet(x, N))))
print("imaginaariosa < 1e-12:", bool(np.max(np.abs(suora_d.imag)) < 1e-12))
print(f"arvo pisteessä 0 (raja-arvo) = 2N + 1 = {2 * N + 1},"
      f" pisteessä 1e-6: {dirichlet(np.array([1e-6]), N)[0]:.6f}")
# @loppu dirichlet
