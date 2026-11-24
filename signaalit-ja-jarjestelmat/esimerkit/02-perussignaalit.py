"""Perussignaalit ja aikaindeksin operaatiot NumPy-taulukoina."""

import numpy as np
import numpy.typing as npt

Jono = npt.NDArray[np.float64]


def nayta(nimi: str, x: Jono) -> None:
    print(f"{nimi:<10}", " ".join(f"{v:6.3f}" for v in x + 0.0))


# @alku perus
n = np.arange(-3, 6)                      # indeksit -3..5
delta = (n == 0).astype(float)            # yksikköimpulssi
askel = (n >= 0).astype(float)            # yksikköaskel u[n]
eksp = 0.5**n * askel                     # 0.5^n u[n]
print("n         ", " ".join(f"{v:6d}" for v in n))
nayta("delta[n]", delta)
nayta("u[n]", askel)
nayta("0.5^n u[n]", eksp)
# @loppu perus

# @alku operaatiot
nayta("u[n-2]", (n - 2 >= 0).astype(float))     # viive kahdella
nayta("u[-n]", (-n >= 0).astype(float))         # aikakääntö
nayta("u-u[n-3]", askel - (n - 3 >= 0))         # pulssi n = 0..2
# Jokainen jono on summa siirrettyjä impulsseja: x[n] = sum x[k] d[n-k].
x = np.array([2.0, -1.0, 0.5])
koottu = sum(x[k] * (n - k == 0) for k in range(len(x)))
nayta("koottu", np.asarray(koottu, dtype=float))
# @loppu operaatiot
