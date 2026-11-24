"""Pythonin silmukat, NumPyn alkiolaskut ja BLAS-kirjaston matriisitulo."""

import time

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


# @alku silmukat
def tulo_silmukoin(a: Matriisi, b: Matriisi) -> Matriisi:
    n, m = a.shape[0], b.shape[1]
    c = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            s = 0.0
            for k in range(a.shape[1]):
                s += a[i, k] * b[k, j]
            c[i, j] = s
    return c
# @loppu silmukat


def aika(f: object, *argumentit: object) -> tuple[float, Matriisi]:
    assert callable(f)
    t0 = time.perf_counter()
    tulos = f(*argumentit)
    return time.perf_counter() - t0, tulos


n = 60
idx = np.arange(n * n, dtype=np.float64).reshape(n, n)
a, b = np.sin(idx * 0.01), np.cos(idx * 0.02)
t_silmukka, c1 = aika(tulo_silmukoin, a, b)
np.matmul(a, b)                          # lämmittely: kirjaston alustus
# @alku blas
t_blas, c2 = aika(np.matmul, a, b)       # kutsuu BLAS-kirjaston dgemm
# @loppu blas
print("samat:", bool(np.allclose(c1, c2)))
print("BLAS yli 50 kertaa nopeampi:", t_silmukka > 50 * t_blas)
# @alku tyyppi
a32 = a.astype(np.float32)
print(a.nbytes, a32.nbytes, (a32 @ a32).dtype)
print("float32-ero alle 1e-4:",
      bool(np.max(np.abs(a32 @ a32 - a @ a)) < 1e-4))
# @loppu tyyppi
