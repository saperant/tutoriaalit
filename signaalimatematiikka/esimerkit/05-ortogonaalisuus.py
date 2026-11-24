"""Kompleksisten eksponenttien ortogonaalisuus."""


import numpy as np


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku ortogonaalisuus
M = 64                                 # näytteitä jaksolla [0, 2 pi)
t = 2 * np.pi * np.arange(M) / M


def sisatulo(m: int, n: int) -> complex:
    """(1/2pi) int_0^2pi e^(imt) conj(e^(int)) dt jaksollisena keskiarvona."""
    return complex(np.mean(np.exp(1j * m * t) * np.conj(np.exp(1j * n * t))))


print("|<e_m, e_n>|" + "".join(f"{'n=' + str(n):>7}" for n in range(-2, 3)))
for m in range(-2, 3):
    rivi = "".join(f"{abs(sisatulo(m, n)):7.3f}" for n in range(-2, 3))
    print(f"{'m=' + str(m):>10}{rivi}")
kerroin = 2 * np.mean(np.sin(3 * t) * np.sin(3 * t))
risti = 2 * np.mean(np.sin(3 * t) * np.cos(5 * t))
print(f"2<sin 3t, sin 3t> = {kerroin:.3f}, 2<sin 3t, cos 5t> ="
      f" {round(risti, 12) + 0.0:.3f}")
print("huom. m - n = 64 palaa lähtöön:", kl(sisatulo(65, 1), 3))
# @loppu ortogonaalisuus
