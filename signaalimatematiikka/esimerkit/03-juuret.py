"""Ykkösen juuret."""


import numpy as np


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku juuret
N = 8
juuret = np.exp(2j * np.pi * np.arange(N) / N)
for k in range(3):
    print(f"w^{k} = {kl(complex(juuret[k]))}")
print(f"kaikki |w^k| = 1: {bool(np.allclose(np.abs(juuret), 1))}")
print(f"w^{N} = 1: {bool(np.isclose(juuret[1] ** N, 1))}")
print(f"summa: {kl(complex(np.sum(juuret)))}")
for m in [1, 2, 3, 8]:
    s = np.sum(juuret ** m)
    print(f"sum w^(k*{m}) = {kl(complex(s), 3)}")
# @loppu juuret
